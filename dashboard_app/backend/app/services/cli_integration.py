"""
Service for integrating with the audit_log_cli and policy_validator_cli tools.
"""

import asyncio
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal  # Added for background task session
from app.services.audit_log import import_audit_log_from_csv
from app.services.policy_validation import import_validation_results_from_csv


async def run_audit_log_cli(input_path: str, output_format: str = "csv", verbose: bool = False) -> Tuple[bool, str, Optional[str]]:
    """
    Run the audit_log_cli tool to scan files and generate a report.
    Runs the subprocess in a separate thread to avoid blocking asyncio event loop.
    """
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, f"audit_log_report.{output_format}")

    cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "audit_log_cli", "app", "main.py"))

    command = ["python", cli_path, "--input", input_path, "--output", output_file, "--format", output_format]

    if verbose:
        command.append("--verbose")

    try:
        process = await asyncio.to_thread(subprocess.run, command, capture_output=True, text=True, check=False)
        if process.returncode == 0:
            return True, output_file, None
        else:
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                pass
            return False, "", f"Error running audit_log_cli (exit code {process.returncode}): {process.stderr or process.stdout}"
    except Exception as e:
        try:
            shutil.rmtree(temp_dir)
        except OSError:
            pass
        return False, "", f"Exception running audit_log_cli: {str(e)}"


async def run_policy_validator_cli(
    input_path: str, policy_file: Optional[str] = None, output_format: str = "csv", verbose: bool = False
) -> Tuple[bool, str, Optional[str]]:
    """
    Run the policy_validator_cli tool to validate metadata against policies.
    Runs the subprocess in a separate thread to avoid blocking asyncio event loop.
    """
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, f"policy_validation_report.{output_format}")

    cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "policy_validator_cli", "app", "main.py"))

    command = ["python", cli_path, "--input", input_path, "--output", output_file, "--format", output_format]

    if policy_file:
        command.extend(["--policy", policy_file])

    if verbose:
        command.append("--verbose")

    try:
        process = await asyncio.to_thread(subprocess.run, command, capture_output=True, text=True, check=False)
        if process.returncode == 0:
            return True, output_file, None
        else:
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                pass
            return False, "", f"Error running policy_validator_cli (exit code {process.returncode}): {process.stderr or process.stdout}"
    except Exception as e:
        try:
            shutil.rmtree(temp_dir)
        except OSError:
            pass
        return False, "", f"Exception running policy_validator_cli: {str(e)}"


async def import_cli_results_to_db(
    db: AsyncSession, audit_log_file: Optional[str] = None, policy_validation_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Import results from CLI tools into the database.
    """
    result = {"audit_logs_imported": 0, "validation_results_imported": 0, "errors": []}

    if audit_log_file and os.path.exists(audit_log_file):
        try:
            count = await import_audit_log_from_csv(db, audit_log_file)
            result["audit_logs_imported"] = count
        except Exception as e:
            result["errors"].append(f"Error importing audit logs: {str(e)}")

    if policy_validation_file and os.path.exists(policy_validation_file):
        try:
            count = await import_validation_results_from_csv(db, policy_validation_file)
            result["validation_results_imported"] = count
        except Exception as e:
            result["errors"].append(f"Error importing validation results: {str(e)}")

    return result


async def run_scheduled_scan(input_path: str, policy_file: Optional[str] = None, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
    """
    Run a scheduled scan using both CLI tools and import results.
    Manages its own DB session if one is not provided (for background tasks).
    """
    scan_result = {
        "scan_time": datetime.now().isoformat(),
        "input_path": input_path,
        "audit_log": {"success": False, "imported": 0, "output_file": None, "error": None},
        "policy_validation": {"success": False, "imported": 0, "output_file": None, "error": None},
    }

    audit_log_temp_dir_local = None
    policy_validation_temp_dir_local = None

    async def _execute_scan_logic(session: AsyncSession):
        nonlocal audit_log_temp_dir_local, policy_validation_temp_dir_local

        try:
            audit_success, audit_file_path, audit_error = await run_audit_log_cli(input_path=input_path, output_format="csv", verbose=True)
            scan_result["audit_log"]["success"] = audit_success
            if audit_success:
                scan_result["audit_log"]["output_file"] = audit_file_path
                if audit_file_path:
                    audit_log_temp_dir_local = os.path.dirname(audit_file_path)
            else:
                scan_result["audit_log"]["error"] = audit_error

            policy_success, policy_val_file_path, policy_error = await run_policy_validator_cli(
                input_path=input_path, policy_file=policy_file, output_format="csv", verbose=True
            )
            scan_result["policy_validation"]["success"] = policy_success
            if policy_success:
                scan_result["policy_validation"]["output_file"] = policy_val_file_path
                if policy_val_file_path:
                    policy_validation_temp_dir_local = os.path.dirname(policy_val_file_path)
            else:
                scan_result["policy_validation"]["error"] = policy_error

            if audit_success or policy_success:
                import_result_data = await import_cli_results_to_db(
                    db=session,
                    audit_log_file=audit_file_path if audit_success else None,
                    policy_validation_file=policy_val_file_path if policy_success else None,
                )

                scan_result["audit_log"]["imported"] = import_result_data.get("audit_logs_imported", 0)
                scan_result["policy_validation"]["imported"] = import_result_data.get("validation_results_imported", 0)

                if import_result_data.get("errors"):
                    for err_msg in import_result_data["errors"]:
                        if "audit_log" in err_msg.lower() and not scan_result["audit_log"]["error"]:
                            scan_result["audit_log"]["error"] = err_msg
                        elif "validation" in err_msg.lower() and not scan_result["policy_validation"]["error"]:
                            scan_result["policy_validation"]["error"] = err_msg
        except Exception as e_inner:
            print(f"Error during _execute_scan_logic: {e_inner}")
            general_error_key = "scan_execution_error"
            error_msg_val = f"Exception during scan execution: {str(e_inner)}"
            if not scan_result["audit_log"]["error"] and not scan_result["policy_validation"]["error"]:
                scan_result[general_error_key] = error_msg_val
            elif general_error_key not in scan_result:
                scan_result[general_error_key] = error_msg_val

    try:
        if db:
            await _execute_scan_logic(db)
        else:
            async with AsyncSessionLocal() as session:
                await _execute_scan_logic(session)
    except Exception as e_outer:
        print(f"Error in run_scheduled_scan session management or top-level call: {e_outer}")
        general_error_key = "scan_session_error"
        error_msg_val = f"Exception in scan session or top-level call: {str(e_outer)}"
        if not scan_result["audit_log"]["error"] and not scan_result["policy_validation"]["error"] and general_error_key not in scan_result:
            scan_result[general_error_key] = error_msg_val

    finally:
        if audit_log_temp_dir_local:
            try:
                shutil.rmtree(audit_log_temp_dir_local)
            except OSError as e:
                cleanup_error_msg = f"Cleanup error for audit log temp dir: {str(e)}"
                if not scan_result["audit_log"]["error"]:
                    scan_result["audit_log"]["error"] = cleanup_error_msg
                else:
                    scan_result["audit_log"]["error"] += f"; {cleanup_error_msg}"

        if policy_validation_temp_dir_local and policy_validation_temp_dir_local != audit_log_temp_dir_local:
            try:
                shutil.rmtree(policy_validation_temp_dir_local)
            except OSError as e:
                cleanup_error_msg = f"Cleanup error for policy validation temp dir: {str(e)}"
                if not scan_result["policy_validation"]["error"]:
                    scan_result["policy_validation"]["error"] = cleanup_error_msg
                else:
                    scan_result["policy_validation"]["error"] += f"; {cleanup_error_msg}"

    return scan_result

# Agent Continuation Prompt

Use this prompt to continue implementation work efficiently:

---

**Continue implementation of the microservices migration. Focus on:**

1. **Implementation First** - Build the next service in the migration plan
2. **Direct Documentation** - Only update service READMEs and progress tracker
3. **No Summary Docs** - Skip session summaries and executive overviews
4. **Progress Tracking** - Update based on implementation vs master plan, not timeline
5. **Follow Patterns** - Use existing services (auth-service, key-service) as templates
6. **Quality Focus** - Production-ready code, proper error handling, comprehensive tests

**Check progress:** `docs/architecture/MICROSERVICES_PROGRESS.md`
**Master plan:** `docs/architecture/MICROSERVICES_MIGRATION_PLAN.md`
**Global rules:** See user_rules in memory and `agents.md`

**Next service to build:** [Check progress tracker for next pending service]

Work through implementation systematically until master plan is complete.

---

**This prompt ensures:**
- Focus on code over documentation
- Consistent quality and patterns
- Clear progress tracking
- Efficient use of context

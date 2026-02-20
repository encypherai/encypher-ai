const res = await fetch("http://localhost:3000/api/auth/callback/credentials", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  body: JSON.stringify({
    email: "test_mfa_user@encypherai.com",
    password: "Password123!",
    redirect: "false",
    csrfToken: "mock"
  })
});
const text = await res.text();
console.log("Status:", res.status);
console.log("Body:", text);

const res = await fetch("http://localhost:3000/api/auth/callback/credentials", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
  },
  body: new URLSearchParams({
    email: "test_mfa_user@encypherai.com", // Need a user with MFA or valid credentials to test
    password: "Password123!",
    redirect: "false"
  })
});
const text = await res.text();
console.log(text);

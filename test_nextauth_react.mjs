import fetch from "node-fetch";

const res = await fetch("http://localhost:3000/api/auth/callback/credentials", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  body: JSON.stringify({
    email: "test@example.com",
    password: "password123",
    redirect: "false",
    csrfToken: "mock" // Might need csrf token
  })
});
const text = await res.text();
console.log("Status:", res.status);
console.log("Body:", text);

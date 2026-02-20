import fetch from "node-fetch";

const res = await fetch("http://localhost:3000/api/auth/callback/credentials", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded"
  },
  body: new URLSearchParams({
    email: "test@example.com",
    password: "password123",
    redirect: "false"
  })
});
const data = await res.json();
console.log(data);

const email = "test_5fc8a3@encypher.com";
const password = "Password123!";

const res = await fetch("http://localhost:3000/api/auth/callback/credentials", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
  },
  body: new URLSearchParams({
    email,
    password,
    redirect: "false"
  })
});
const data = await res.json();
console.log("Status:", res.status);
console.log("Body:", data);

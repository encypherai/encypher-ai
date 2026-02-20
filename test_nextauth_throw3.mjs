const res = await fetch("http://localhost:3000/api/auth/callback/credentials", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
  },
  body: new URLSearchParams({
    email: "test@example.com",
    password: "password123",
    redirect: "false"
  })
});
const text = await res.text();
try {
  console.log(JSON.parse(text));
} catch (e) {
  console.log("Not JSON:", text);
}

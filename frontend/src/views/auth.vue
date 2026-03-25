<template>
  <div class="auth-container">

    <h1>White Market</h1>

    <!-- LOGIN -->
    <div v-if="page === 'login'">
      <h2>Login</h2>

      <input v-model="email" placeholder="Email">
      <input v-model="password" type="password" placeholder="Password">

      <button @click="login">Login</button>
      <button class="secondary" @click="page = 'register'">
        Register
      </button>
    </div>

    <!-- REGISTER -->
    <div v-else>
      <h2>Register</h2>

      <input v-model="email" placeholder="School Email">
      <input v-model="password" type="password" placeholder="Password">

      <select v-model="role">
        <option disabled value="">Select Role</option>
        <option value="buyer">Buyer</option>
        <option value="seller">Seller</option>
      </select>

      <button @click="register">Register</button>
      <button class="secondary" @click="page = 'login'">
        Back to Login
      </button>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      page: "login",
      email: "",
      password: "",
      role: ""
    };
  },

  methods: {
    register() {
      if (!this.email.endsWith("@school.edu")) {
        alert("Use school email");
        return;
      }

      const users = JSON.parse(localStorage.getItem("users")) || [];

      users.push({
        email: this.email,
        password: this.password,
        role: this.role
      });

      localStorage.setItem("users", JSON.stringify(users));

      alert("Registered successfully!");
      this.page = "login";
    },

    login() {
      const users = JSON.parse(localStorage.getItem("users")) || [];

      const user = users.find(
        u => u.email === this.email && u.password === this.password
      );

      if (!user) return alert("Invalid credentials");

      localStorage.setItem("currentUser", JSON.stringify(user));
      this.$router.push("/");
    }
  }
};
</script>

<style>
.auth-container {
  max-width: 340px;
  margin: 100px auto;
  padding: 30px 25px;
  background: white;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.auth-container h2 {
  margin-bottom: 15px;
}

.auth-container button {
  margin-top: 10px;
}

input, select {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

button {
  width: 100%;
  margin-top: 10px;
}

.secondary {
  background: #ddd;
  color: #333;
}
</style>
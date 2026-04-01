<template>
  <div class="auth-page">
    <div class="auth-card">

      <div class="auth-brand">
        <span class="brand-icon">🛒</span>
        <h1>White Market</h1>
        <p class="brand-sub">Your university marketplace</p>
      </div>

      <!-- LOGIN -->
      <div v-if="page === 'login'" class="auth-form">
        <h2>Welcome back</h2>

        <div class="field">
          <label>School Email</label>
          <input v-model="email" placeholder="you@school.edu" type="email" />
        </div>
        <div class="field">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="••••••••" />
        </div>

        <button class="btn-primary" @click="login">Login</button>
        <button class="btn-secondary" @click="page = 'register'">
          Create an account
        </button>
      </div>

      <!-- REGISTER -->
      <div v-else class="auth-form">
        <h2>Create account</h2>

        <div class="field">
          <label>School Email</label>
          <input v-model="email" placeholder="you@school.edu" type="email" />
        </div>
        <div class="field">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="••••••••" />
        </div>
        <div class="field">
          <label>I am a...</label>
          <select v-model="role">
            <option disabled value="">Select role</option>
            <option value="buyer">Buyer</option>
            <option value="seller">Seller</option>
          </select>
        </div>

        <button class="btn-primary" @click="register">Register</button>
        <button class="btn-secondary" @click="page = 'login'">
          Back to Login
        </button>
      </div>

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
        alert("Please use your school email (@school.edu)");
        return;
      }
      if (!this.role) {
        alert("Please select a role");
        return;
      }

      const users = JSON.parse(localStorage.getItem("users")) || [];
      if (users.find(u => u.email === this.email)) {
        alert("An account with this email already exists.");
        return;
      }

      users.push({ email: this.email, password: this.password, role: this.role });
      localStorage.setItem("users", JSON.stringify(users));

      alert("Registered successfully!");
      this.page = "login";
    },

    login() {
      const users = JSON.parse(localStorage.getItem("users")) || [];
      const user = users.find(
        u => u.email === this.email && u.password === this.password
      );

      if (!user) return alert("Invalid email or password.");

      localStorage.setItem("currentUser", JSON.stringify(user));
      this.$router.push("/");
    }
  }
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: #03120E;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-card {
  background: #fff;
  border-radius: 20px;
  padding: 40px 36px;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4);
}

.auth-brand {
  text-align: center;
  margin-bottom: 28px;
}

.brand-icon {
  font-size: 36px;
}

.auth-brand h1 {
  font-size: 24px;
  font-weight: 800;
  color: #03120E;
  margin: 6px 0 4px;
}

.brand-sub {
  font-size: 13px;
  color: #888;
  margin: 0;
}

.auth-form h2 {
  font-size: 18px;
  font-weight: 700;
  color: #111;
  margin-bottom: 20px;
}

.field {
  margin-bottom: 14px;
}

.field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #555;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.field input,
.field select {
  width: 100%;
  padding: 11px 14px;
  border-radius: 8px;
  border: 1.5px solid #ddd;
  font-size: 14px;
  box-sizing: border-box;
  margin: 0;
  transition: border-color 0.2s;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: #03120E;
  box-shadow: 0 0 0 3px rgba(3, 18, 14, 0.08);
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: #03120E;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
  transition: background 0.2s, transform 0.15s;
}

.btn-primary:hover {
  background: #0a2a23;
  transform: translateY(-1px);
}

.btn-secondary {
  width: 100%;
  padding: 11px;
  background: #f4f4f4;
  color: #444;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 10px;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #e8e8e8;
  transform: none;
}
</style>
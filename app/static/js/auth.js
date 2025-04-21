// Import Firebase Auth instance from local config
import { auth } from "./firebase-config.js";

// Import necessary Firebase Auth functions from CDN
import {
  createUserWithEmailAndPassword,
  updateProfile,
  signInWithEmailAndPassword
} from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

// ===============================
// Signup Function
// ===============================
window.signup = async function () {
  // Get user input values
  const firstName = document.getElementById("first-name").value;
  const lastName = document.getElementById("last-name").value;
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  const errorMessage = document.getElementById("signup-error-message");

  try {
    // Create user with Firebase Authentication
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Set user's full name in profile
    await updateProfile(user, { displayName: `${firstName} ${lastName}` });

    // Retrieve ID token from Firebase
    const idToken = await user.getIdToken();
    console.log("Generated Firebase ID Token:", idToken); 
    
    // Send token and additional data to backend for verification
    const response = await fetch("/verify_login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idToken, first_name: firstName, last_name: lastName })
    });

    const data = await response.json();

    // Redirect to dashboard if backend confirms success
    if (data.success) {
      window.location.href = "/dashboard";
    } else {
      throw new Error("Sign-up verification failed!");
    }
  } catch (error) {
    // Display error message on sign-up failure
    console.error("Sign-up error:", error);
    errorMessage.innerText = error.message;
  }
};

// ===============================
// Login Function
// ===============================
window.login = async function () {
  // Get user input values
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;
  const errorMessage = document.getElementById("login-error-message");

  try {
    // Sign in user with Firebase Authentication
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const idToken = await userCredential.user.getIdToken();

    // Send ID token to backend for verification
    const response = await fetch("/verify_login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idToken })
    });
      
    const data = await response.json();
    console.log("Server Response:", data);  

    // Redirect to dashboard if verified
    if (data.success) {
      window.location.href = "/dashboard";
    } else {
      errorMessage.innerText = "Login failed!";
    }
  } catch (error) {
    // Display login error
    errorMessage.innerText = error.message;
  }
};

// ===============================
// Attach login function to login form submit
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();
      login();
    });
  }
});

// ===============================
// Attach signup function to signup form submit
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", (event) => {
      event.preventDefault();
      signup(); 
    });
  }
});

// Ensure signup function is globally accessible
window.signup = signup;

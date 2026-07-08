// =============================
// PROFILE PAGE SCRIPT
// PneumoAI
// =============================

const API_BASE = "/api";
const token = localStorage.getItem("accessToken");
const user = JSON.parse(localStorage.getItem("user") || "{}");

// ── Redirect if not logged in ──
if (!token) {
    window.location.href = "/";
}

// =============================
// INIT
// =============================
document.addEventListener("DOMContentLoaded", init);

async function init() {
    populateFromStorage();
    await loadProfile();
    await loadStats();
    bindEvents();
}

// =============================
// SAFE ELEMENT HELPER
// =============================
function el(id) {
    return document.getElementById(id);
}

function setText(id, value) {
    const element = el(id);
    if (element) element.innerText = (value !== null && value !== undefined && value !== '') ? value : "—";
}

function setValue(id, value) {
    const element = el(id);
    if (element) element.value = value || "";
}

// =============================
// POPULATE FROM LOCALSTORAGE
// (instant load before API responds)
// =============================
function populateFromStorage() {
    if (!user) return;

    setText("profileName", user.fullName);
    setText("profileRole", "User");
    setValue("fullName", user.fullName);
    setValue("username", user.username);
    setValue("email", user.emailId);
    setValue("mobile", user.mobileNumber);

    // Topbar avatar
    const avatar = document.querySelector(".topbar-avatar");
    if (avatar && user.fullName) {
        avatar.textContent = user.fullName
            .split(" ")
            .map(n => n[0])
            .join("")
            .substring(0, 2)
            .toUpperCase();
    }

    // Last login
    if (user.lastLogin) {
        const date = new Date(user.lastLogin).toLocaleString();
        setText("lastLogin", date);
        setText("loginActivity", date);
    }
}

// =============================
// LOAD PROFILE FROM BACKEND
// =============================
async function loadProfile() {
    try {
        const userId = user.id;
        if (!userId) return;

        const res = await fetch(`${API_BASE}/auth/profile?user_id=${userId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (res.status === 401) {
            localStorage.clear();
            window.location.href = "/";
            return;
        }

        if (!res.ok) return;

        const data = await res.json();

        // Support both direct response and wrapped response
        const u = data.data || data;

        // Sidebar
        setText("profileName", u.full_name);
        setText("profileRole", u.role_id === 1 ? "Admin" : "User");

        // Form fields
        setValue("fullName", u.full_name);
        setValue("username", u.username);
        setValue("email", u.email_id);
        setValue("mobile", u.mobile_number);
        setValue("role", u.role_id === 1 ? "Admin" : "User");
        setValue("accountStatus", u.is_active ? "Active" : "Inactive");

        // Account info
        setText("userId", u.id);
        setText("usernameInfo", u.username ? "@" + u.username : "—");
        setText("roleInfo", u.role_id === 1 ? "Admin" : "User");

        if (u.created_on) {
            const since = new Date(u.created_on).toLocaleDateString();
            setText("createdOn", since);
            setText("memberSince", since);
        }

        if (u.updated_on) {
            setText("updatedOn", new Date(u.updated_on).toLocaleString());
            setText("profileActivity", new Date(u.updated_on).toLocaleString());
        }

        if (u.last_login) {
            const loginDate = new Date(u.last_login).toLocaleString();
            setText("lastLogin", loginDate);
            setText("loginActivity", loginDate);
        }

        // Update localStorage with fresh data
        const updatedUser = { ...user };
        updatedUser.fullName = u.full_name;
        updatedUser.mobileNumber = u.mobile_number;
        localStorage.setItem("user", JSON.stringify(updatedUser));

    } catch (err) {
        console.error("Profile load error:", err);
    }
}

// =============================
// LOAD STATS
// =============================
async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/stats`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) return;

        const stats = await res.json();

        setText("totalScans", stats.totalScans);
        setText("normalCases", stats.healthyCases);
        setText("pneumoniaCases", stats.pneumoniaCases);
        setText("averageConfidence", stats.averageConfidence + "%");

        // Recent prediction activity
        if (stats.recentScans && stats.recentScans.length > 0) {
            const latest = stats.recentScans[0];
            setText("predictionActivity", new Date(latest.predictionDate).toLocaleString());
        }

    } catch (err) {
        console.error("Stats load error:", err);
    }
}

// =============================
// BIND EVENTS
// =============================
function bindEvents() {

    // Refresh button
    el("refreshProfileBtn")?.addEventListener("click", async () => {
        await loadProfile();
        await loadStats();
    });

    // Profile form submit
    el("profileForm")?.addEventListener("submit", updateProfile);

    // Change password button → open modal
    el("changePasswordBtn")?.addEventListener("click", () => {
        const modal = el("passwordModal");
        if (modal) modal.style.display = "flex";
    });

    // Close modal
    el("closePasswordModal")?.addEventListener("click", closeModal);
    el("cancelPasswordBtn")?.addEventListener("click", closeModal);

    // Click outside modal to close
    el("passwordModal")?.addEventListener("click", function(e) {
        if (e.target === this) closeModal();
    });

    // Password form submit
    el("passwordForm")?.addEventListener("submit", changePassword);

    // Logout — sidebar button
    el("logoutBtn")?.addEventListener("click", async function(e) {
        e.preventDefault();
        const refreshToken = localStorage.getItem("refreshToken");
        await fetch(`${API_BASE}/auth/logout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ refreshToken })
        });
        localStorage.clear();
        window.location.href = "/";
    });
}

// =============================
// UPDATE PROFILE
// =============================
async function updateProfile(e) {
    e.preventDefault();

    const btn = e.target.querySelector("button[type='submit']");
    const fullName     = el("fullName")?.value.trim();
    const mobileNumber = el("mobile")?.value.trim();

    if (!fullName) {
        alert("Full name is required.");
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    }

    try {
        const userId = user.id;
        const res = await fetch(`${API_BASE}/auth/profile?user_id=${userId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                fullName:      fullName,
                mobileNumber:  mobileNumber
            })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || "Update failed.");
            return;
        }

        // Update localStorage
        const updatedUser = { ...user };
        updatedUser.fullName = fullName;
        updatedUser.mobileNumber = mobileNumber;
        localStorage.setItem("user", JSON.stringify(updatedUser));

        // Update sidebar name + avatar
        setText("profileName", fullName);
        const initials = fullName.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
        const avatar = document.querySelector(".topbar-avatar");
        if (avatar) avatar.textContent = initials;

        alert("Profile updated successfully.");

    } catch (err) {
        console.error("Update error:", err);
        alert("Cannot connect to server.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-floppy-disk"></i> Save Changes';
        }
    }
}

// =============================
// CHANGE PASSWORD
// =============================
async function changePassword(e) {
    e.preventDefault();

    const oldPassword     = el("oldPassword")?.value;
    const newPassword     = el("newPassword")?.value;
    const confirmPassword = el("confirmPassword")?.value;

    if (!oldPassword || !newPassword || !confirmPassword) {
        alert("All fields are required.");
        return;
    }

    if (newPassword !== confirmPassword) {
        alert("New passwords do not match.");
        return;
    }

    if (newPassword.length < 6) {
        alert("New password must be at least 6 characters.");
        return;
    }

    const btn = e.target.querySelector("button[type='submit']");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    }

    try {
        const userId = user.id;
        const res = await fetch(`${API_BASE}/auth/change-password?user_id=${userId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                oldPassword: oldPassword,
                newPassword: newPassword
            })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || "Password change failed.");
            return;
        }

        alert("Password changed successfully.");
        closeModal();

        el("oldPassword").value = "";
        el("newPassword").value = "";
        el("confirmPassword").value = "";

    } catch (err) {
        console.error("Password error:", err);
        alert("Cannot connect to server.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-key"></i> Update Password';
        }
    }
}

// =============================
// CLOSE MODAL
// =============================
function closeModal() {
    const modal = el("passwordModal");
    if (modal) modal.style.display = "none";
}
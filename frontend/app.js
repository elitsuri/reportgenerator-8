/**
 * reportgenerator - Frontend Application
 * ReportGenerator: Automated report generation with PDF, Excel, and email delivery
 */

const API_BASE = "http://localhost:8000/api/v1";

class ApiClient {
    constructor() {
        this.token = localStorage.getItem("access_token");
    }

    async request(method, path, data = null) {
        const headers = { "Content-Type": "application/json" };
        if (this.token) headers["Authorization"] = `Bearer ${this.token}`;
        const res = await fetch(`${API_BASE}${path}`, {
            method,
            headers,
            body: data ? JSON.stringify(data) : null,
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(err.detail || "Request failed");
        }
        if (res.status === 204) return null;
        return res.json();
    }

    async login(email, password) {
        const form = new URLSearchParams({ username: email, password });
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: form,
        });
        if (!res.ok) throw new Error("Invalid credentials");
        const data = await res.json();
        this.token = data.access_token;
        localStorage.setItem("access_token", this.token);
        return data;
    }

    async register(email, password, fullName) {
        return this.request("POST", "/auth/register", { email, password, full_name: fullName });
    }

    async getItems() { return this.request("GET", "/items"); }
    async createItem(title, description) { return this.request("POST", "/items", { title, description }); }
    async deleteItem(id) { return this.request("DELETE", `/items/${id}`); }

    logout() {
        this.token = null;
        localStorage.removeItem("access_token");
    }
}

const api = new ApiClient();

function showModal(content) {
    document.getElementById("modalBody").innerHTML = content;
    document.getElementById("modal").classList.remove("hidden");
}

function hideModal() {
    document.getElementById("modal").classList.add("hidden");
}

function showLoginForm() {
    showModal(`
        <h2>Login</h2>
        <form id="loginForm">
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="loginEmail" required placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="loginPassword" required>
            </div>
            <div id="loginError" class="error hidden"></div>
            <button type="submit" class="btn btn-primary w-full">Login</button>
        </form>
    `);
    document.getElementById("loginForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            await api.login(
                document.getElementById("loginEmail").value,
                document.getElementById("loginPassword").value
            );
            hideModal();
            renderDashboard();
        } catch (err) {
            document.getElementById("loginError").textContent = err.message;
            document.getElementById("loginError").classList.remove("hidden");
        }
    });
}

function renderDashboard() {
    document.getElementById("nav").innerHTML = `
        <span class="nav-user">Welcome!</span>
        <button class="btn btn-secondary" id="logoutBtn">Logout</button>
        <button class="btn btn-primary" id="addItemBtn">+ Add Item</button>
    `;
    document.getElementById("logoutBtn").addEventListener("click", () => {
        api.logout();
        location.reload();
    });
    document.getElementById("addItemBtn").addEventListener("click", showAddItemForm);
    loadItems();
}

async function loadItems() {
    try {
        const items = await api.getItems();
        const main = document.getElementById("mainContent");
        main.innerHTML = `
            <div class="container">
                <h2>Your Items</h2>
                <div class="items-grid" id="itemsGrid">
                    ${items.length === 0 ? '<p class="empty-state">No items yet. Create your first one!</p>' :
                        items.map(item => `
                            <div class="item-card" data-id="${item.id}">
                                <h3>${item.title}</h3>
                                <p>${item.description || "No description"}</p>
                                <button class="btn btn-danger btn-sm delete-btn" data-id="${item.id}">Delete</button>
                            </div>
                        `).join("")
                    }
                </div>
            </div>
        `;
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = e.target.dataset.id;
                await api.deleteItem(id);
                loadItems();
            });
        });
    } catch (err) {
        console.error("Failed to load items:", err);
    }
}

function showAddItemForm() {
    showModal(`
        <h2>Add New Item</h2>
        <form id="addItemForm">
            <div class="form-group">
                <label>Title</label>
                <input type="text" id="itemTitle" required placeholder="Item title">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="itemDesc" rows="3" placeholder="Optional description"></textarea>
            </div>
            <button type="submit" class="btn btn-primary w-full">Create Item</button>
        </form>
    `);
    document.getElementById("addItemForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        await api.createItem(
            document.getElementById("itemTitle").value,
            document.getElementById("itemDesc").value
        );
        hideModal();
        loadItems();
    });
}

// Init
document.getElementById("loginBtn")?.addEventListener("click", showLoginForm);
document.getElementById("registerBtn")?.addEventListener("click", () => {
    showModal(`
        <h2>Create Account</h2>
        <form id="regForm">
            <div class="form-group"><label>Full Name</label>
                <input type="text" id="regName" placeholder="Your name"></div>
            <div class="form-group"><label>Email</label>
                <input type="email" id="regEmail" required></div>
            <div class="form-group"><label>Password</label>
                <input type="password" id="regPass" required></div>
            <div id="regError" class="error hidden"></div>
            <button type="submit" class="btn btn-primary w-full">Register</button>
        </form>
    `);
    document.getElementById("regForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
            await api.register(
                document.getElementById("regEmail").value,
                document.getElementById("regPass").value,
                document.getElementById("regName").value,
            );
            await api.login(
                document.getElementById("regEmail").value,
                document.getElementById("regPass").value,
            );
            hideModal();
            renderDashboard();
        } catch (err) {
            document.getElementById("regError").textContent = err.message;
            document.getElementById("regError").classList.remove("hidden");
        }
    });
});
document.getElementById("getStartedBtn")?.addEventListener("click", showLoginForm);
document.getElementById("modalClose")?.addEventListener("click", hideModal);
document.getElementById("modalOverlay")?.addEventListener("click", hideModal);

if (api.token) renderDashboard();

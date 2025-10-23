// グローバル変数
let currentUser = null;
let authToken = null;
let allMaterials = [];
let allRecipes = [];
let allProducts = [];

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
    authToken = localStorage.getItem('authToken');
    if (authToken) {
        showAppSection();
        loadInitialData();
    } else {
        showAuthSection();
    }
    setupEventListeners();
});

// イベントリスナーの設定
function setupEventListeners() {
    // 認証タブ
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchAuthTab(e.target.dataset.tab);
        });
    });

    // 認証フォーム
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // ナビゲーションタブ
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            switchSection(e.target.dataset.section);
        });
    });

    // 追加ボタン
    document.getElementById('add-material-btn').addEventListener('click', () => showMaterialForm());
    document.getElementById('add-recipe-btn').addEventListener('click', () => showRecipeForm());
    document.getElementById('add-fixed-cost-btn').addEventListener('click', () => showFixedCostForm());
    document.getElementById('add-product-btn').addEventListener('click', () => showProductForm());

    // ラベル印刷ボタン
    document.getElementById('manage-label-settings-btn').addEventListener('click', () => showLabelSettingsManager());
    document.getElementById('print-labels-btn').addEventListener('click', () => printSelectedLabels());
}

// 認証タブの切り替え
function switchAuthTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`${tab}-form`).classList.add('active');
}

// セクションの切り替え
function switchSection(section) {
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    document.getElementById(`${section}-section`).classList.add('active');
    loadSectionData(section);
}

// 認証セクション表示
function showAuthSection() {
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('app-section').style.display = 'none';
}

// アプリセクション表示
function showAppSection() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('app-section').style.display = 'block';
}

// ログイン
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showMessage('ログインに成功しました', 'success');
            showAppSection();
            loadInitialData();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'ログインに失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

// 登録
async function handleRegister(e) {
    e.preventDefault();
    const storeId = document.getElementById('register-store-id').value;
    const storeName = document.getElementById('register-store-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ store_id: storeId, store_name: storeName, email, password })
        });

        if (response.ok) {
            showMessage('登録に成功しました。ログインしてください。', 'success');
            switchAuthTab('login');
            document.getElementById('registerForm').reset();
        } else {
            const error = await response.json();
            showMessage(error.detail || '登録に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

// ログアウト
function handleLogout() {
    authToken = null;
    localStorage.removeItem('authToken');
    showMessage('ログアウトしました', 'info');
    showAuthSection();
}

// 初期データ読み込み
async function loadInitialData() {
    loadSectionData('materials');
}

// セクションデータ読み込み
async function loadSectionData(section) {
    switch (section) {
        case 'materials': await loadMaterials(); break;
        case 'recipes': await loadRecipes(); break;
        case 'fixed-costs': await loadFixedCosts(); break;
        case 'products': await loadProducts(); break;
        case 'labels': await loadLabelProducts(); break;
    }
}

// === 材料管理 ===
async function loadMaterials() {
    try {
        const response = await fetch('/api/materials/', {
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        if (response.ok) {
            allMaterials = await response.json();
            displayMaterials(allMaterials);
        }
    } catch (error) {
        showMessage('材料データの取得に失敗しました', 'error');
    }
}

function displayMaterials(materials) {
    const container = document.getElementById('materials-list');
    container.innerHTML = '';

    if (materials.length === 0) {
        container.innerHTML = '<p>材料がまだ登録されていません。</p>';
        return;
    }

    materials.forEach(material => {
        const item = document.createElement('div');
        item.className = 'data-item';
        item.innerHTML = `
            <div class="data-item-header">
                <div class="data-item-title">${material.name}</div>
                <div class="data-item-actions">
                    <button class="btn btn-secondary" onclick="editMaterial(${material.id})">編集</button>
                    <button class="btn btn-danger" onclick="deleteMaterial(${material.id})">削除</button>
                </div>
            </div>
            <div>
                <p>購入価格: ¥${material.purchase_price.toLocaleString()}</p>
                <p>購入容量: ${material.purchase_quantity} ${material.unit}</p>
                <p><strong>単価: ¥${material.unit_price.toFixed(2)} / ${material.unit}</strong></p>
            </div>
        `;
        container.appendChild(item);
    });
}

function showMaterialForm(material = null) {
    const isEdit = material !== null;
    const formHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>${isEdit ? '材料を編集' : '新規材料追加'}</h3>
                <form id="material-form" onsubmit="saveMaterial(event, ${material ? material.id : 'null'})">
                    <div class="form-group">
                        <label>材料名 *</label>
                        <input type="text" id="material-name" value="${material ? material.name : ''}" required>
                    </div>
                    <div class="form-group">
                        <label>購入金額 (円) *</label>
                        <input type="number" id="material-price" step="0.01" value="${material ? material.purchase_price : ''}" required>
                    </div>
                    <div class="form-group">
                        <label>購入容量 *</label>
                        <input type="number" id="material-quantity" step="0.01" value="${material ? material.purchase_quantity : ''}" required>
                    </div>
                    <div class="form-group">
                        <label>単位 *</label>
                        <input type="text" id="material-unit" value="${material ? material.unit : ''}" placeholder="例: g, ml, 個" required>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">保存</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">キャンセル</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
}

async function saveMaterial(e, id) {
    e.preventDefault();
    const data = {
        name: document.getElementById('material-name').value,
        purchase_price: parseFloat(document.getElementById('material-price').value),
        purchase_quantity: parseFloat(document.getElementById('material-quantity').value),
        unit: document.getElementById('material-unit').value
    };

    try {
        const url = id ? `/api/materials/${id}` : '/api/materials/';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showMessage(id ? '材料を更新しました' : '材料を追加しました', 'success');
            closeModal();
            loadMaterials();
        } else {
            const error = await response.json();
            showMessage(error.detail || '保存に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

async function editMaterial(id) {
    const material = allMaterials.find(m => m.id === id);
    if (material) showMaterialForm(material);
}

async function deleteMaterial(id) {
    if (!confirm('この材料を削除してもよろしいですか?')) return;

    try {
        const response = await fetch(`/api/materials/${id}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${authToken}`}
        });

        if (response.ok) {
            showMessage('材料を削除しました', 'success');
            loadMaterials();
        } else {
            showMessage('削除に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

// === レシピ管理 ===
async function loadRecipes() {
    try {
        const response = await fetch('/api/recipes/', {
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        if (response.ok) {
            allRecipes = await response.json();
            displayRecipes(allRecipes);
        }
    } catch (error) {
        showMessage('レシピデータの取得に失敗しました', 'error');
    }
}

function displayRecipes(recipes) {
    const container = document.getElementById('recipes-list');
    container.innerHTML = '';

    if (recipes.length === 0) {
        container.innerHTML = '<p>レシピがまだ登録されていません。</p>';
        return;
    }

    recipes.forEach(recipe => {
        const item = document.createElement('div');
        item.className = 'data-item';
        const materialsHtml = recipe.materials.map(m =>
            `${m.material_name}: ${m.quantity} ${m.material_unit} (¥${m.cost.toFixed(2)})`
        ).join('<br>');

        item.innerHTML = `
            <div class="data-item-header">
                <div class="data-item-title">${recipe.name}</div>
                <div class="data-item-actions">
                    <button class="btn btn-secondary" onclick="editRecipe(${recipe.id})">編集</button>
                    <button class="btn btn-danger" onclick="deleteRecipe(${recipe.id})">削除</button>
                </div>
            </div>
            <div>
                ${recipe.description ? `<p>${recipe.description}</p>` : ''}
                <p><strong>材料費合計: ¥${recipe.material_cost.toFixed(2)}</strong></p>
                <details>
                    <summary>使用材料</summary>
                    <div style="margin-top: 10px;">${materialsHtml || '材料なし'}</div>
                </details>
            </div>
        `;
        container.appendChild(item);
    });
}

function showRecipeForm(recipe = null) {
    if (allMaterials.length === 0) {
        showMessage('先に材料を登録してください', 'error');
        return;
    }

    const isEdit = recipe !== null;
    const materialsOptions = allMaterials.map(m =>
        `<option value="${m.id}">${m.name} (¥${m.unit_price.toFixed(2)}/${m.unit})</option>`
    ).join('');

    const formHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>${isEdit ? 'レシピを編集' : '新規レシピ追加'}</h3>
                <form id="recipe-form" onsubmit="saveRecipe(event, ${recipe ? recipe.id : 'null'})">
                    <div class="form-group">
                        <label>レシピ名 *</label>
                        <input type="text" id="recipe-name" value="${recipe ? recipe.name : ''}" required>
                    </div>
                    <div class="form-group">
                        <label>説明</label>
                        <textarea id="recipe-description" rows="2">${recipe ? (recipe.description || '') : ''}</textarea>
                    </div>
                    <div class="form-group">
                        <label>使用材料</label>
                        <div id="recipe-materials-list"></div>
                        <button type="button" class="btn btn-secondary" onclick="addRecipeMaterial()">材料を追加</button>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">保存</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">キャンセル</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);

    window.recipeMaterialsOptions = materialsOptions;
    if (recipe && recipe.materials) {
        recipe.materials.forEach(m => addRecipeMaterial(m.material_id, m.quantity));
    }
}

function addRecipeMaterial(materialId = '', quantity = '') {
    const container = document.getElementById('recipe-materials-list');
    const index = container.children.length;
    const div = document.createElement('div');
    div.className = 'material-row';
    div.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px;';
    div.innerHTML = `
        <select class="recipe-material-id" style="flex: 2;" required>
            <option value="">材料を選択</option>
            ${window.recipeMaterialsOptions}
        </select>
        <input type="number" class="recipe-material-quantity" placeholder="使用量" step="0.01" value="${quantity}" style="flex: 1;" required>
        <button type="button" class="btn btn-danger" onclick="this.parentElement.remove()" style="padding: 8px 12px;">削除</button>
    `;
    container.appendChild(div);
    if (materialId) {
        div.querySelector('.recipe-material-id').value = materialId;
    }
}

async function saveRecipe(e, id) {
    e.preventDefault();
    const materials = Array.from(document.querySelectorAll('.material-row')).map(row => ({
        material_id: parseInt(row.querySelector('.recipe-material-id').value),
        quantity: parseFloat(row.querySelector('.recipe-material-quantity').value)
    }));

    const data = {
        name: document.getElementById('recipe-name').value,
        description: document.getElementById('recipe-description').value || null,
        materials
    };

    try {
        const url = id ? `/api/recipes/${id}` : '/api/recipes/';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showMessage(id ? 'レシピを更新しました' : 'レシピを追加しました', 'success');
            closeModal();
            loadRecipes();
        } else {
            const error = await response.json();
            showMessage(error.detail || '保存に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

async function editRecipe(id) {
    const recipe = allRecipes.find(r => r.id === id);
    if (recipe) showRecipeForm(recipe);
}

async function deleteRecipe(id) {
    if (!confirm('このレシピを削除してもよろしいですか?')) return;

    try {
        const response = await fetch(`/api/recipes/${id}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${authToken}`}
        });

        if (response.ok) {
            showMessage('レシピを削除しました', 'success');
            loadRecipes();
        } else {
            showMessage('削除に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

// === 固定費管理 ===
async function loadFixedCosts() {
    try {
        const [costsRes, totalRes] = await Promise.all([
            fetch('/api/fixed-costs/', {headers: {'Authorization': `Bearer ${authToken}`}}),
            fetch('/api/fixed-costs/total', {headers: {'Authorization': `Bearer ${authToken}`}})
        ]);

        if (costsRes.ok && totalRes.ok) {
            const costs = await costsRes.json();
            const total = await totalRes.json();
            displayFixedCosts(costs, total.total_monthly_fixed_cost);
        }
    } catch (error) {
        showMessage('固定費データの取得に失敗しました', 'error');
    }
}

function displayFixedCosts(costs, total) {
    const summary = document.getElementById('fixed-costs-summary');
    summary.innerHTML = `
        <h3>月次固定費合計</h3>
        <p>¥${total.toLocaleString()}</p>
    `;

    const container = document.getElementById('fixed-costs-list');
    container.innerHTML = '';

    if (costs.length === 0) {
        container.innerHTML = '<p>固定費がまだ登録されていません。</p>';
        return;
    }

    costs.forEach(cost => {
        const item = document.createElement('div');
        item.className = 'data-item';
        item.innerHTML = `
            <div class="data-item-header">
                <div class="data-item-title">${cost.name} ${cost.is_active ? '' : '(無効)'}</div>
                <div class="data-item-actions">
                    <button class="btn btn-secondary" onclick="editFixedCost(${cost.id}, '${cost.name}', ${cost.monthly_amount}, ${cost.is_active})">編集</button>
                    <button class="btn btn-danger" onclick="deleteFixedCost(${cost.id})">削除</button>
                </div>
            </div>
            <div>
                <p>月額: ¥${cost.monthly_amount.toLocaleString()}</p>
                <p>状態: ${cost.is_active ? '有効（計算に含む）' : '無効'}</p>
            </div>
        `;
        container.appendChild(item);
    });
}

function showFixedCostForm(cost = null) {
    const isEdit = cost !== null;
    const formHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>${isEdit ? '固定費を編集' : '固定費項目を追加'}</h3>
                <form id="fixed-cost-form" onsubmit="saveFixedCost(event, ${cost ? cost.id : 'null'})">
                    <div class="form-group">
                        <label>項目名 *</label>
                        <input type="text" id="fc-name" value="${cost ? cost.name : ''}" placeholder="例: 家賃、光熱費" required>
                    </div>
                    <div class="form-group">
                        <label>月額 (円) *</label>
                        <input type="number" id="fc-amount" step="0.01" value="${cost ? cost.monthly_amount : ''}" required>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="fc-active" ${cost ? (cost.is_active ? 'checked' : '') : 'checked'}>
                            有効（原価計算に含める）
                        </label>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">保存</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">キャンセル</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
}

async function saveFixedCost(e, id) {
    e.preventDefault();
    const data = {
        name: document.getElementById('fc-name').value,
        monthly_amount: parseFloat(document.getElementById('fc-amount').value),
        is_active: document.getElementById('fc-active').checked
    };

    try {
        const url = id ? `/api/fixed-costs/${id}` : '/api/fixed-costs/';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showMessage(id ? '固定費を更新しました' : '固定費を追加しました', 'success');
            closeModal();
            loadFixedCosts();
        } else {
            const error = await response.json();
            showMessage(error.detail || '保存に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

async function editFixedCost(id, name, amount, isActive) {
    showFixedCostForm({id, name, monthly_amount: amount, is_active: isActive});
}

async function deleteFixedCost(id) {
    if (!confirm('この固定費を削除してもよろしいですか?')) return;

    try {
        const response = await fetch(`/api/fixed-costs/${id}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${authToken}`}
        });

        if (response.ok) {
            showMessage('固定費を削除しました', 'success');
            loadFixedCosts();
        } else {
            showMessage('削除に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

// === 商品管理 ===
async function loadProducts() {
    try {
        const response = await fetch('/api/products/', {
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        if (response.ok) {
            allProducts = await response.json();
            displayProducts(allProducts);
        }
    } catch (error) {
        showMessage('商品データの取得に失敗しました', 'error');
    }
}

function displayProducts(products) {
    const container = document.getElementById('products-list');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<p>商品がまだ登録されていません。</p>';
        return;
    }

    products.forEach(product => {
        const item = document.createElement('div');
        item.className = 'data-item';
        item.innerHTML = `
            <div class="data-item-header">
                <div class="data-item-title">${product.name}</div>
                <div class="data-item-actions">
                    <button class="btn btn-secondary" onclick="editProduct(${product.id})">編集</button>
                    <button class="btn btn-danger" onclick="deleteProduct(${product.id})">削除</button>
                </div>
            </div>
            <div>
                <p>材料費: ¥${product.material_cost.toFixed(2)}</p>
                <p>固定費/個: ¥${product.fixed_cost_per_unit.toFixed(2)} ${product.include_fixed_cost ? '(含む)' : '(含まない)'}</p>
                <p><strong>総原価: ¥${product.total_cost.toFixed(2)}</strong></p>
                <p>利益率: ${product.profit_margin}%</p>
                <p>推奨販売価格: ¥${Math.ceil(product.suggested_price)}</p>
                ${product.selling_price ? `
                    <p><strong>実際の販売価格: ¥${product.selling_price}</strong></p>
                    <p>実際の利益: ¥${product.actual_profit_amount.toFixed(2)} (${product.actual_profit_margin.toFixed(1)}%)</p>
                ` : ''}
            </div>
        `;
        container.appendChild(item);
    });
}

function showProductForm(product = null) {
    if (allRecipes.length === 0) {
        showMessage('先にレシピを登録してください', 'error');
        return;
    }

    const isEdit = product !== null;
    const recipesOptions = allRecipes.map(r =>
        `<option value="${r.id}" ${product && product.recipe_id === r.id ? 'selected' : ''}>${r.name} (¥${r.material_cost.toFixed(2)})</option>`
    ).join('');

    const formHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>${isEdit ? '商品を編集' : '新規商品追加'}</h3>
                <form id="product-form" onsubmit="saveProduct(event, ${product ? product.id : 'null'})">
                    <div class="form-group">
                        <label>商品名 *</label>
                        <input type="text" id="product-name" value="${product ? product.name : ''}" required>
                    </div>
                    <div class="form-group">
                        <label>レシピ</label>
                        <select id="product-recipe">
                            <option value="">なし</option>
                            ${recipesOptions}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="product-include-fixed" ${product ? (product.include_fixed_cost ? 'checked' : '') : ''}>
                            固定費を含める
                        </label>
                    </div>
                    <div class="form-group">
                        <label>利益率 (%) *</label>
                        <input type="number" id="product-margin" step="0.1" value="${product ? product.profit_margin : 30}" required>
                    </div>
                    <div class="form-group">
                        <label>販売価格 (円) - オプション</label>
                        <input type="number" id="product-price" step="1" value="${product && product.selling_price ? product.selling_price : ''}" placeholder="推奨価格を使用する場合は空欄">
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">保存</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">キャンセル</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
}

async function saveProduct(e, id) {
    e.preventDefault();
    const recipeId = document.getElementById('product-recipe').value;
    const price = document.getElementById('product-price').value;

    const data = {
        name: document.getElementById('product-name').value,
        recipe_id: recipeId ? parseInt(recipeId) : null,
        include_fixed_cost: document.getElementById('product-include-fixed').checked,
        profit_margin: parseFloat(document.getElementById('product-margin').value),
        selling_price: price ? parseFloat(price) : null
    };

    try {
        const url = id ? `/api/products/${id}` : '/api/products/';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showMessage(id ? '商品を更新しました' : '商品を追加しました', 'success');
            closeModal();
            loadProducts();
        } else {
            const error = await response.json();
            showMessage(error.detail || '保存に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

async function editProduct(id) {
    const product = allProducts.find(p => p.id === id);
    if (product) showProductForm(product);
}

async function deleteProduct(id) {
    if (!confirm('この商品を削除してもよろしいですか?')) return;

    try {
        const response = await fetch(`/api/products/${id}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${authToken}`}
        });

        if (response.ok) {
            showMessage('商品を削除しました', 'success');
            loadProducts();
        } else {
            showMessage('削除に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

// === ラベル印刷 ===
let selectedProductIds = [];

async function loadLabelProducts() {
    try {
        const response = await fetch('/api/products/', {
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        if (response.ok) {
            allProducts = await response.json();
            displayLabelProducts(allProducts);
        }
    } catch (error) {
        showMessage('商品データの取得に失敗しました', 'error');
    }
}

function displayLabelProducts(products) {
    const container = document.getElementById('label-products-list');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<p>商品がまだ登録されていません。先に商品を登録してください。</p>';
        return;
    }

    products.forEach(product => {
        const item = document.createElement('div');
        item.className = 'data-item';
        item.style.cursor = 'pointer';

        const isSelected = selectedProductIds.includes(product.id);
        if (isSelected) {
            item.style.borderLeft = '4px solid #28a745';
            item.style.backgroundColor = '#e8f5e9';
        }

        item.innerHTML = `
            <div class="data-item-header">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <input type="checkbox" class="product-checkbox" data-product-id="${product.id}"
                           ${isSelected ? 'checked' : ''}
                           style="width: 20px; height: 20px; cursor: pointer;">
                    <div class="data-item-title">${product.name}</div>
                </div>
            </div>
            <div>
                <p>販売価格: ${product.selling_price ? '¥' + product.selling_price : '未設定'}</p>
                <p>レシピ: ${product.recipe_id ? 'あり' : 'なし'}</p>
            </div>
        `;

        // チェックボックスのクリックイベント
        const checkbox = item.querySelector('.product-checkbox');
        checkbox.addEventListener('change', (e) => {
            e.stopPropagation();
            toggleProductSelection(product.id);
        });

        // カード全体のクリックでもチェックボックスをトグル
        item.addEventListener('click', (e) => {
            if (e.target !== checkbox) {
                checkbox.checked = !checkbox.checked;
                toggleProductSelection(product.id);
            }
        });

        container.appendChild(item);
    });

    // 選択数を表示
    const summary = document.createElement('div');
    summary.style.cssText = 'margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px;';
    summary.innerHTML = `<strong>選択中: ${selectedProductIds.length}個の商品</strong>`;
    container.insertBefore(summary, container.firstChild);
}

function toggleProductSelection(productId) {
    const index = selectedProductIds.indexOf(productId);
    if (index > -1) {
        selectedProductIds.splice(index, 1);
    } else {
        selectedProductIds.push(productId);
    }
    displayLabelProducts(allProducts);
}

async function printSelectedLabels() {
    if (selectedProductIds.length === 0) {
        showMessage('印刷する商品を選択してください', 'error');
        return;
    }

    // 印刷設定ダイアログを表示
    showPrintDialog();
}

function showPrintDialog() {
    const formHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>ラベル印刷設定</h3>
                <form id="print-form" onsubmit="executePrint(event)">
                    <div class="form-group">
                        <label>ラベルサイズ (mm)</label>
                        <div style="display: flex; gap: 10px;">
                            <input type="number" id="label-width" placeholder="幅" value="50" step="0.1" required style="flex: 1;">
                            <input type="number" id="label-height" placeholder="高さ" value="30" step="0.1" required style="flex: 1;">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>余白 (mm)</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <input type="number" id="margin-top" placeholder="上" value="10" step="0.1" required>
                            <input type="number" id="margin-bottom" placeholder="下" value="10" step="0.1" required>
                            <input type="number" id="margin-left" placeholder="左" value="10" step="0.1" required>
                            <input type="number" id="margin-right" placeholder="右" value="10" step="0.1" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>賞味期限 (オプション)</label>
                        <input type="date" id="expiry-date">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="show-price" checked>
                            価格を表示
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="show-ingredients" checked>
                            原材料を表示
                        </label>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-success">PDFをダウンロード</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">キャンセル</button>
                    </div>
                </form>
                <p style="margin-top: 15px; font-size: 0.9rem; color: #666;">
                    選択中: ${selectedProductIds.length}個の商品
                </p>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
}

async function executePrint(e) {
    e.preventDefault();

    const data = {
        product_ids: selectedProductIds,
        expiry_date: document.getElementById('expiry-date').value || null
    };

    try {
        showMessage('PDFを生成中...', 'info');

        const response = await fetch('/api/labels/print', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            // PDFをダウンロード
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `labels_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showMessage('ラベルPDFをダウンロードしました', 'success');
            closeModal();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'PDF生成に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
        console.error(error);
    }
}

// === ラベル設定管理 ===
let allLabelSettings = [];
let defaultLabelSetting = null;

async function showLabelSettingsManager() {
    await loadLabelSettings();
    displayLabelSettingsManager();
}

async function loadLabelSettings() {
    try {
        const response = await fetch('/api/labels/settings', {
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        if (response.ok) {
            allLabelSettings = await response.json();
        }

        // デフォルト設定も取得を試みる
        try {
            const defaultResponse = await fetch('/api/labels/settings/default', {
                headers: {'Authorization': `Bearer ${authToken}`}
            });
            if (defaultResponse.ok) {
                defaultLabelSetting = await defaultResponse.json();
            }
        } catch (e) {
            // デフォルト設定がない場合は無視
        }
    } catch (error) {
        showMessage('ラベル設定の取得に失敗しました', 'error');
    }
}

function displayLabelSettingsManager() {
    const formHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()" style="max-width: 800px;">
                <h3>ラベル設定管理</h3>
                <button class="btn btn-primary" onclick="showLabelSettingForm()" style="margin-bottom: 20px;">新規プリセット追加</button>

                <div id="label-settings-list"></div>

                <div class="form-actions" style="margin-top: 20px;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">閉じる</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
    displayLabelSettingsList();
}

function displayLabelSettingsList() {
    const container = document.getElementById('label-settings-list');
    container.innerHTML = '';

    if (allLabelSettings.length === 0) {
        container.innerHTML = '<p>ラベル設定がまだ登録されていません。</p>';
        return;
    }

    allLabelSettings.forEach(setting => {
        const item = document.createElement('div');
        item.className = 'data-item';
        item.style.marginBottom = '15px';

        const labelsPerSheet = setting.labels_per_sheet || 0;

        item.innerHTML = `
            <div class="data-item-header">
                <div class="data-item-title">
                    ${setting.preset_name}
                    ${setting.is_default ? '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8rem; margin-left: 10px;">デフォルト</span>' : ''}
                </div>
                <div class="data-item-actions">
                    ${!setting.is_default ? `<button class="btn btn-secondary" onclick="setDefaultLabelSetting(${setting.id})">デフォルトに設定</button>` : ''}
                    <button class="btn btn-secondary" onclick="editLabelSetting(${setting.id})">編集</button>
                    <button class="btn btn-danger" onclick="deleteLabelSetting(${setting.id})">削除</button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">
                <div>
                    <p><strong>ラベルサイズ:</strong> ${setting.label_width} × ${setting.label_height} mm</p>
                    <p><strong>余白:</strong> 上${setting.margin_top} 下${setting.margin_bottom} 左${setting.margin_left} 右${setting.margin_right} mm</p>
                    <p><strong>1シートあたり:</strong> 約${labelsPerSheet}枚</p>
                </div>
                <div>
                    <p><strong>表示オプション:</strong></p>
                    <ul style="margin-left: 20px; font-size: 0.9rem;">
                        <li>${setting.show_price ? '✓' : '✗'} 価格</li>
                        <li>${setting.show_ingredients ? '✓' : '✗'} 原材料</li>
                        <li>${setting.show_expiry_date ? '✓' : '✗'} 賞味期限</li>
                        <li>${setting.show_store_name ? '✓' : '✗'} 店舗名</li>
                    </ul>
                </div>
            </div>
        `;
        container.appendChild(item);
    });
}

function showLabelSettingForm(setting = null) {
    const isEdit = setting !== null;
    const formHtml = `
        <div class="modal-overlay" onclick="closeAllModals()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>${isEdit ? 'ラベル設定を編集' : '新規ラベル設定'}</h3>
                <form id="label-setting-form" onsubmit="saveLabelSetting(event, ${setting ? setting.id : 'null'})">
                    <div class="form-group">
                        <label>プリセット名 *</label>
                        <input type="text" id="ls-preset-name" value="${setting ? setting.preset_name : ''}" placeholder="例: 標準ラベル" required>
                    </div>

                    <div class="form-group">
                        <label>ラベルサイズ (mm) *</label>
                        <div style="display: flex; gap: 10px;">
                            <input type="number" id="ls-width" placeholder="幅" value="${setting ? setting.label_width : 50}" step="0.1" required style="flex: 1;">
                            <input type="number" id="ls-height" placeholder="高さ" value="${setting ? setting.label_height : 30}" step="0.1" required style="flex: 1;">
                        </div>
                    </div>

                    <div class="form-group">
                        <label>余白 (mm) *</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <input type="number" id="ls-margin-top" placeholder="上" value="${setting ? setting.margin_top : 10}" step="0.1" required>
                            <input type="number" id="ls-margin-bottom" placeholder="下" value="${setting ? setting.margin_bottom : 10}" step="0.1" required>
                            <input type="number" id="ls-margin-left" placeholder="左" value="${setting ? setting.margin_left : 10}" step="0.1" required>
                            <input type="number" id="ls-margin-right" placeholder="右" value="${setting ? setting.margin_right : 10}" step="0.1" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>表示オプション</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <label><input type="checkbox" id="ls-show-price" ${setting ? (setting.show_price ? 'checked' : '') : 'checked'}> 価格を表示</label>
                            <label><input type="checkbox" id="ls-show-ingredients" ${setting ? (setting.show_ingredients ? 'checked' : '') : 'checked'}> 原材料を表示</label>
                            <label><input type="checkbox" id="ls-show-expiry" ${setting ? (setting.show_expiry_date ? 'checked' : '') : ''}> 賞味期限を表示</label>
                            <label><input type="checkbox" id="ls-show-store" ${setting ? (setting.show_store_name ? 'checked' : '') : 'checked'}> 店舗名を表示</label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="ls-is-default" ${setting ? (setting.is_default ? 'checked' : '') : ''}>
                            デフォルト設定にする
                        </label>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">保存</button>
                        <button type="button" class="btn btn-secondary" onclick="closeTopModal()">キャンセル</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
}

async function saveLabelSetting(e, id) {
    e.preventDefault();

    const data = {
        preset_name: document.getElementById('ls-preset-name').value,
        label_width: parseFloat(document.getElementById('ls-width').value),
        label_height: parseFloat(document.getElementById('ls-height').value),
        margin_top: parseFloat(document.getElementById('ls-margin-top').value),
        margin_bottom: parseFloat(document.getElementById('ls-margin-bottom').value),
        margin_left: parseFloat(document.getElementById('ls-margin-left').value),
        margin_right: parseFloat(document.getElementById('ls-margin-right').value),
        show_price: document.getElementById('ls-show-price').checked,
        show_ingredients: document.getElementById('ls-show-ingredients').checked,
        show_expiry_date: document.getElementById('ls-show-expiry').checked,
        show_store_name: document.getElementById('ls-show-store').checked,
        show_logo: false,
        logo_path: null,
        is_default: document.getElementById('ls-is-default').checked
    };

    try {
        const url = id ? `/api/labels/settings/${id}` : '/api/labels/settings';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showMessage(id ? 'ラベル設定を更新しました' : 'ラベル設定を追加しました', 'success');
            closeTopModal();
            await loadLabelSettings();
            displayLabelSettingsList();
        } else {
            const error = await response.json();
            showMessage(error.detail || '保存に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

async function editLabelSetting(id) {
    const setting = allLabelSettings.find(s => s.id === id);
    if (setting) showLabelSettingForm(setting);
}

async function deleteLabelSetting(id) {
    if (!confirm('このラベル設定を削除してもよろしいですか?')) return;

    try {
        const response = await fetch(`/api/labels/settings/${id}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${authToken}`}
        });

        if (response.ok) {
            showMessage('ラベル設定を削除しました', 'success');
            await loadLabelSettings();
            displayLabelSettingsList();
        } else {
            showMessage('削除に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

async function setDefaultLabelSetting(id) {
    const setting = allLabelSettings.find(s => s.id === id);
    if (!setting) return;

    // is_defaultをtrueにして更新
    try {
        const response = await fetch(`/api/labels/settings/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...setting,
                is_default: true
            })
        });

        if (response.ok) {
            showMessage('デフォルト設定を更新しました', 'success');
            await loadLabelSettings();
            displayLabelSettingsList();
        } else {
            showMessage('更新に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('ネットワークエラーが発生しました', 'error');
    }
}

// 印刷ダイアログでデフォルト設定を使用
async function showPrintDialogWithSettings() {
    if (selectedProductIds.length === 0) {
        showMessage('印刷する商品を選択してください', 'error');
        return;
    }

    // デフォルト設定を取得
    let defaultSetting = null;
    try {
        const response = await fetch('/api/labels/settings/default', {
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        if (response.ok) {
            defaultSetting = await response.json();
        }
    } catch (e) {
        // デフォルト設定がない場合はデフォルト値を使用
    }

    const width = defaultSetting ? defaultSetting.label_width : 50;
    const height = defaultSetting ? defaultSetting.label_height : 30;
    const marginTop = defaultSetting ? defaultSetting.margin_top : 10;
    const marginBottom = defaultSetting ? defaultSetting.margin_bottom : 10;
    const marginLeft = defaultSetting ? defaultSetting.margin_left : 10;
    const marginRight = defaultSetting ? defaultSetting.margin_right : 10;
    const showPrice = defaultSetting ? defaultSetting.show_price : true;
    const showIngredients = defaultSetting ? defaultSetting.show_ingredients : true;

    const formHtml = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <h3>ラベル印刷設定</h3>
                ${defaultSetting ? `<p style="color: #666; margin-bottom: 15px;">使用中のプリセット: <strong>${defaultSetting.preset_name}</strong></p>` : ''}
                <form id="print-form" onsubmit="executePrint(event)">
                    <div class="form-group">
                        <label>ラベルサイズ (mm)</label>
                        <div style="display: flex; gap: 10px;">
                            <input type="number" id="label-width" placeholder="幅" value="${width}" step="0.1" required style="flex: 1;">
                            <input type="number" id="label-height" placeholder="高さ" value="${height}" step="0.1" required style="flex: 1;">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>余白 (mm)</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <input type="number" id="margin-top" placeholder="上" value="${marginTop}" step="0.1" required>
                            <input type="number" id="margin-bottom" placeholder="下" value="${marginBottom}" step="0.1" required>
                            <input type="number" id="margin-left" placeholder="左" value="${marginLeft}" step="0.1" required>
                            <input type="number" id="margin-right" placeholder="右" value="${marginRight}" step="0.1" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>賞味期限 (オプション)</label>
                        <input type="date" id="expiry-date">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="show-price" ${showPrice ? 'checked' : ''}>
                            価格を表示
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="show-ingredients" ${showIngredients ? 'checked' : ''}>
                            原材料を表示
                        </label>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-success">PDFをダウンロード</button>
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">キャンセル</button>
                    </div>
                </form>
                <p style="margin-top: 15px; font-size: 0.9rem; color: #666;">
                    選択中: ${selectedProductIds.length}個の商品
                </p>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', formHtml);
}

// === ユーティリティ ===
function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

function closeTopModal() {
    const modals = document.querySelectorAll('.modal-overlay');
    if (modals.length > 0) {
        modals[modals.length - 1].remove();
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => modal.remove());
}

function showMessage(message, type = 'info') {
    const container = document.getElementById('message-container');
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    messageEl.textContent = message;
    container.appendChild(messageEl);
    setTimeout(() => messageEl.remove(), 3000);
}

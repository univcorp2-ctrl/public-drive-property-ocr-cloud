let sessionToken = null;

const $ = (id) => document.getElementById(id);

async function initLiff() {
  const status = $("liffStatus");
  try {
    const config = await fetch("/api/config").then((res) => res.json());
    if (!config.liff_id) {
      status.textContent = "LIFF未設定 / Web表示";
      return;
    }
    if (!window.liff) {
      status.textContent = "LIFF SDK未読込";
      return;
    }
    await window.liff.init({ liffId: config.liff_id });
    status.textContent = window.liff.isInClient() ? "LINE内で起動中" : "外部ブラウザ";
  } catch (error) {
    status.textContent = "LIFF初期化失敗";
    console.error(error);
  }
}

async function authenticate() {
  const noteId = $("noteId").value;
  const button = $("authButton");
  button.disabled = true;
  $("authMessage").textContent = "認証中です...";
  try {
    const response = await fetch("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note_id: noteId }),
    });
    if (!response.ok) throw new Error("認証に失敗しました");
    const data = await response.json();
    sessionToken = data.token;
    $("authMessage").textContent = `${data.note_id} で認証しました。`;
    $("chatCard").classList.remove("hidden");
  } catch (error) {
    $("authMessage").textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

async function analyze() {
  const file = $("fileInput").files[0];
  if (!sessionToken) {
    alert("先にnote ID認証をしてください。");
    return;
  }
  if (!file) {
    alert("ファイルを選択してください。");
    return;
  }
  const button = $("analyzeButton");
  button.disabled = true;
  button.textContent = "OCRを実行しています...";
  const form = new FormData();
  form.append("token", sessionToken);
  form.append("file", file);
  form.append("manual_text", $("manualText").value);

  try {
    const response = await fetch("/api/analyze", { method: "POST", body: form });
    if (!response.ok) throw new Error("判定に失敗しました");
    const data = await response.json();
    $("resultJson").textContent = JSON.stringify(data.result, null, 2);
    $("csvLink").href = data.exports.csv;
    $("xlsxLink").href = data.exports.xlsx;
    $("txtLink").href = data.exports.txt;
    $("resultCard").classList.remove("hidden");
  } catch (error) {
    alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "OCRとボリューム判定を実行";
  }
}

$("authButton").addEventListener("click", authenticate);
$("analyzeButton").addEventListener("click", analyze);
initLiff();

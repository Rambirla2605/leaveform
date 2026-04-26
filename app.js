
/* ================= LOGIN ================= */

function login() {
  let email = document.getElementById("email")?.value;
  let password = document.getElementById("password")?.value;

  let studentPattern = /^25ec\d{3}@drngpit\.ac\.in$/;
  let staffEmail = "iam.rambirla@gmail.com";

  if (!email || !password) {
    alert("Enter email & password");
    return;
  }

  if (!(studentPattern.test(email) || email === staffEmail)) {
    alert("Use valid student mail or staff mail");
    return;
  }

  let stored = localStorage.getItem(email);

  // First login
  if (!stored) {
    if (password === "stu123") {
      localStorage.setItem("tempUser", email);
      window.location.href = "change-password.html";
    } else {
      alert("Use default password: stu123");
    }
    return;
  }

  // Normal login
  if (password === stored) {
    localStorage.setItem("currentUser", email);

    if (email === staffEmail) {
      window.location.href = "staff.html";
    } else {
      window.location.href = "student-details.html";
    }
  } else {
    alert("Wrong password");
  }
}

/* ================= CHANGE PASSWORD ================= */

function savePass() {
  let newPass = document.getElementById("newPass")?.value;
  let confirm = document.getElementById("confirmPass")?.value;
  let email = localStorage.getItem("tempUser");

  if (!newPass || !confirm) {
    alert("Fill all fields");
    return;
  }

  if (newPass !== confirm) {
    alert("Passwords do not match");
    return;
  }

  localStorage.setItem(email, newPass);
  alert("Password updated");

  window.location.href = "index.html";
}

/* ================= STUDENT DETAILS ================= */

function submitDetails() {
  let name = document.getElementById("name")?.value.toUpperCase();
  let dept = document.getElementById("dept")?.value.toUpperCase();
  let reg = document.getElementById("reg")?.value;

  if (!name || !dept || !reg) {
    alert("Fill all fields");
    return;
  }

  if (reg < 710725106064 || reg > 710725106126) {
    alert("Invalid Register Number");
    return;
  }

  localStorage.setItem("name", name);
  localStorage.setItem("dept", dept);
  localStorage.setItem("reg", reg);

  window.location.href = "calendar.html";
}

/* ================= CALENDAR ================= */

let selectedDates = [];

if (document.querySelector(".days")) {

  const daysTag = document.querySelector(".days"),
  currentDate = document.querySelector(".current-date"),
  prevNextIcon = document.querySelectorAll(".icons span");

  let date = new Date(),
  currYear = date.getFullYear(),
  currMonth = date.getMonth();

  const months = ["January","February","March","April","May","June",
  "July","August","September","October","November","December"];

  function renderCalendar() {

    let firstDay = new Date(currYear, currMonth, 1).getDay();
    let lastDate = new Date(currYear, currMonth + 1, 0).getDate();
    let lastDay = new Date(currYear, currMonth, lastDate).getDay();
    let prevLastDate = new Date(currYear, currMonth, 0).getDate();

    let liTag = "";

    for (let i = firstDay; i > 0; i--) {
      liTag += `<li class="inactive">${prevLastDate - i + 1}</li>`;
    }

    let today = new Date();
    today.setHours(0,0,0,0);

    for (let i = 1; i <= lastDate; i++) {
      let fullDate = new Date(currYear, currMonth, i);
      fullDate.setHours(0,0,0,0);

      let isPast = fullDate < today;
      let formattedDate = fullDate.toISOString().split("T")[0];

      let className = isPast ? "inactive" : "";

      liTag += `<li class="${className}" data-date="${formattedDate}">${i}</li>`;
    }

    for (let i = lastDay; i < 6; i++) {
      liTag += `<li class="inactive">${i - lastDay + 1}</li>`;
    }

    currentDate.innerText = `${months[currMonth]} ${currYear}`;
    daysTag.innerHTML = liTag;

    document.querySelectorAll(".days li").forEach(li => {
      if (!li.classList.contains("inactive")) {
        li.addEventListener("click", () => {

          let date = li.getAttribute("data-date");

          if (selectedDates.includes(date)) {
            selectedDates = selectedDates.filter(d => d !== date);
            li.classList.remove("active");
          } else {
            selectedDates.push(date);
            li.classList.add("active");
          }

        });
      }
    });
  }

  renderCalendar();

  prevNextIcon.forEach(icon => {
    icon.addEventListener("click", () => {
      currMonth = icon.id === "prev" ? currMonth - 1 : currMonth + 1;

      if (currMonth < 0 || currMonth > 11) {
        date = new Date(currYear, currMonth);
        currYear = date.getFullYear();
        currMonth = date.getMonth();
      }

      renderCalendar();
    });
  });

  window.submitLeave = function () {

    let reason = document.getElementById("reason")?.value;
    let reg = localStorage.getItem("reg");
    let name = localStorage.getItem("name");

    if (selectedDates.length === 0 || !reason) {
      alert("Select date(s) & enter reason");
      return;
    }

    let leaves = JSON.parse(localStorage.getItem("leaves")) || [];

    selectedDates.forEach(date => {
      let exists = leaves.some(l => l.reg === reg && l.date === date);

      if (!exists) {
        leaves.push({
          name,
          reg,
          date,
          reason,
          status: "pending"
        });
      }
    });

    localStorage.setItem("leaves", JSON.stringify(leaves));

    alert("Leave Submitted");

    selectedDates = [];
    window.location.href = "index.html";
  };
}

/* ================= STAFF ================= */

function loadStaff() {
  let container = document.getElementById("leaveList");
  if (!container) return;

  let leaves = JSON.parse(localStorage.getItem("leaves")) || [];
  let today = new Date().toISOString().split("T")[0];

  let todayLeaves = leaves.filter(l => l.date === today);

  let todayCountEl = document.getElementById("todayCount");
  if (todayCountEl) {
    todayCountEl.innerText = "Today Leave: " + todayLeaves.length;
  }

  container.innerHTML = "";

  leaves.forEach((l, i) => {
    container.innerHTML += `
      <div class="card">

        <div class="leave-info">
          <p><b>${l.name}</b> (${l.reg})</p>
          <p>${l.date}</p>
          <p>${l.reason}</p>
          <p>Status: <b class="${l.status}">${l.status}</b></p>
        </div>

        <div class="actions">
  ${
    l.status === "pending"
      ? `<button class="approve" onclick="approve(${i})">Approve</button>
         <button class="reject" onclick="reject(${i})">Reject</button>`
      : `<button disabled>${l.status.toUpperCase()}</button>`
  }
</div>

      </div>
    `;
  });

  updateNotification();
}

function approve(i) {
  let leaves = JSON.parse(localStorage.getItem("leaves")) || [];
  if (!leaves[i]) return;

  // ❌ BLOCK if already rejected
  if (leaves[i].status === "rejected") {
    alert("Cannot approve. Leave already rejected.");
    return;
  }

  // ❌ BLOCK if already approved
  if (leaves[i].status === "approved") {
    alert("Already approved.");
    return;
  }

  leaves[i].status = "approved";
  localStorage.setItem("leaves", JSON.stringify(leaves));
  loadStaff();
}

function reject(i) {
  let leaves = JSON.parse(localStorage.getItem("leaves")) || [];
  if (!leaves[i]) return;

  // ❌ BLOCK if already approved
  if (leaves[i].status === "approved") {
    alert("Cannot reject. Leave already approved.");
    return;
  }

  // ❌ BLOCK if already rejected
  if (leaves[i].status === "rejected") {
    alert("Already rejected.");
    return;
  }

  leaves[i].status = "rejected";
  localStorage.setItem("leaves", JSON.stringify(leaves));
  loadStaff();
}
/* ================= NAVIGATION ================= */

function showPage(page) {
  let pages = document.querySelectorAll(".page");

  pages.forEach(p => p.style.display = "none");

  let target = document.getElementById(page);
  if (target) target.style.display = "block";

  if (page === "leaves") loadStaff();
  if (page === "history") loadHistory();
}

window.onload = function () {
  showPage("dashboard");
};

/* ================= HISTORY ================= */

function loadHistory() {
  let container = document.getElementById("historyList");
  if (!container) return;

  let leaves = JSON.parse(localStorage.getItem("leaves")) || [];

  let history = leaves.filter(l =>
    l.status === "approved" || l.status === "rejected"
  );

  container.innerHTML = "";

  history.forEach(l => {
    container.innerHTML += `
      <div class="card">
        <p><b>${l.name}</b> (${l.reg})</p>
        <p>${l.date}</p>
        <p>${l.reason}</p>
        <p>Status: <b class="${l.status}">${l.status}</b></p>
      </div>
    `;
  });
}

/* ================= NOTIFICATION ================= */

function updateNotification() {
  let leaves = JSON.parse(localStorage.getItem("leaves")) || [];
  let pending = leaves.filter(l => l.status === "pending").length;

  let badge = document.getElementById("notifBadge");
  if (badge) badge.innerText = pending > 0 ? `(${pending})` : "";
}

/* ================= LOGOUT ================= */

function logout() {
  localStorage.removeItem("currentUser");
  window.location.href = "index.html";
}

/* ================= INIT ================= */

if (document.getElementById("leaveList")) {
  loadStaff();
}
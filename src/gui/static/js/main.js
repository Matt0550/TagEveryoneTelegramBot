const errorAlert = (message) => {
    window.Telegram.WebApp.HapticFeedback.notificationOccurred("error");
    window.Telegram.WebApp.showAlert(`Error: ${message}`);
}

const leaveGroup = (group_id) => {
    // Confirm
    window.Telegram.WebApp.showConfirm("Are you sure you want to leave this list? You can rejoin at any time with the /in command.", (result) => {
        if (result) {
            fetch("/leaveInListGroup", {
                method: "POST",
                body: JSON.stringify({
                    "init_data": TG_INIT_DATA,
                    "hash": TG_INIT_HASH,
                    "group_id": group_id
                }),
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status !== 200) {
                    if (data.status === 401) {
                        $("#unauthorized").show();
                    }
                    console.log("Error", data.message);
                    errorAlert(data.message);
                    return;
                }
                window.Telegram.WebApp.HapticFeedback.notificationOccurred("success");
                window.Telegram.WebApp.showAlert(`Success: ${data.message}`);
                window.location.reload();
            });
        }
    });
}

const fetchGroups = () => {
    fetch("/getInGroups", {
        method: "POST",
        body: JSON.stringify({
            "init_data": TG_INIT_DATA,
            "hash": TG_INIT_HASH
        }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);

        if (data.status !== 200) {
            if (data.status === 401) {
                $("#unauthorized").show();
            }
            console.log("Error", data.message);
            errorAlert(data.message);
            return;
        }

        if (data.isOwner) {
            window.Telegram.WebApp.MainButton.text = "Admin Panel";
            window.Telegram.WebApp.MainButton.show();

            window.Telegram.WebApp.MainButton.onClick(() => {
                window.Telegram.WebApp.MainButton.showProgress();
                fetchAdminPanel();
            });
        }

        renderGroups(data.groups);
    });
}

const fetchAdminPanel = () => {
    fetch("/getAdminPanel", {
        method: "POST",
        body: JSON.stringify({
            "init_data": TG_INIT_DATA,
            "hash": TG_INIT_HASH
        }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        window.Telegram.WebApp.MainButton.hideProgress();

        if (data.status !== 200) {
            if (data.status === 401) {
                $("#unauthorized").show();
            }
            console.log("Error", data.message);
            errorAlert(data.message);
            return;
        }

        displayAdminLogs(data.logs);
    });
}

const renderGroups = (groups) => {
    const groupListContainer = $("#group-list");
    if (groups.length === 0) {
        groupListContainer.append(`
            <div class="flex flex-row justify-between items-center bg-gray-200 rounded-lg p-4 mb-2">
                <div class="flex flex-col">
                    <h1 class="text-lg font-bold text-gray-700">No groups</h1>
                    <p class="text-sm text-gray-500">You are not included in any tag list. To join a group, use the <b>/in</b> command.</p>
                </div>
            </div>
        `);
    } else {
        groups.forEach(group => {
            groupListContainer.append(`
                <div class="flex flex-row justify-between items-center rounded-lg p-4 mb-2" style="background-color: var(--tg-theme-secondary-bg-color);">
                    <div class="flex flex-col">
                        <h1 class="text-lg font-bold">${group.name}</h1>
                        <p class="text-sm" style="color: var(--tg-theme-hint-color);">${group.members} members</p>
                    </div>
                    <div class="flex flex-row">
                        <button class="text-white font-bold py-2 px-4 rounded" style="background-color: var(--tg-theme-button-color); color: var(--tg-theme-button-text-color)" onclick="leaveGroup(${group.group_id})">
                            Leave list
                        </button>
                    </div>
                </div>
            `);
        });
    }
}

const displayAdminLogs = (logs) => {
    const logListContainer = $("#log-list");
    $("#group-div").hide();
    window.Telegram.WebApp.MainButton.hide();

    window.Telegram.WebApp.BackButton.onClick(() => {
        window.Telegram.WebApp.BackButton.hide();
        window.Telegram.WebApp.MainButton.show();
        $("#group-div").show();
        $("#log-div").hide();
    });

    window.Telegram.WebApp.BackButton.show();

    logListContainer.empty();
    $("#log-count").text(logs.length);

    if (logs.length === 0) {
        logListContainer.append(`
            <div class="flex flex-row justify-between items-center bg-gray-200 rounded-lg p-4 mb-2">
                <div class="flex flex-col">
                    <h1 class="text-lg font-bold text-gray-700">No logs</h1>
                    <p class="text-sm text-gray-500">No logs found.</p>
                </div>
            </div>
        `);
    } else {
        logs.forEach(log => {
            logListContainer.append(`
                <div class="flex flex-row justify-between items-center rounded-lg p-4 mb-2" style="background-color: var(--tg-theme-secondary-bg-color);">
                    <div class="flex flex-col">
                        <h1 class="text-lg font-bold">${log.action}</h1>
                        <p class="text-sm" style="color: var(--tg-theme-hint-color);">${log.description}</p>
                        <p class="text-sm" style="color: var(--tg-theme-hint-color);">${log.datetime}</p>
                        <p class="text-sm" style="color: var(--tg-theme-hint-color);">User ID: ${log.user_id}</p>
                        <p class="text-sm" style="color: var(--tg-theme-hint-color);">Chat ID: ${log.group_id}</p>
                    </div>
                </div>
            `);
        });
    }

    $("#log-div").show();
}

$(document).ready(() => {
    console.log("ready!");
    fetchGroups();
    window.Telegram.WebApp.ready();
});

// Convert key=val to {key: val}
const TG_INIT_DATA_DICT = TG_INIT_DATA.split("&").reduce((acc, curr) => {
    const [key, val] = curr.split("=");
    acc[key] = val;
    return acc;
}, {});

const TG_INIT_HASH = TG_INIT_DATA_DICT.hash;

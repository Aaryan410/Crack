(() => {
    const storageKey = "crack-theme";
    const themes = ["dark", "light", "matrix"];
    const root = document.documentElement;

    function applyTheme(theme) {
        root.dataset.theme = themes.includes(theme) ? theme : "dark";
    }

    try {
        applyTheme(localStorage.getItem(storageKey));
    } catch {
        applyTheme("dark");
    }

    document.addEventListener("DOMContentLoaded", () => {
        const picker = document.querySelector("#theme-picker");

        if (!picker) {
            return;
        }

        picker.value = root.dataset.theme;

        picker.addEventListener("change", () => {
            applyTheme(picker.value);

            try {
                localStorage.setItem(storageKey, root.dataset.theme);
            } catch {

            }
        });
    });
})();
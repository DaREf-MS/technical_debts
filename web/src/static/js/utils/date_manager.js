function generate_date(previousDays = 0) {
    const now = new Date();
    
    // Subtract previousDays
    now.setDate(now.getDate() - previousDays);

    const pad = (n) => n.toString().padStart(2, "0");

    const day = pad(now.getDate());
    const month = pad(now.getMonth() + 1);
    const year = now.getFullYear();
    const hours = pad(now.getHours());
    const minutes = pad(now.getMinutes());

    return `${day}/${month}/${year} ${hours}:${minutes}`;
}
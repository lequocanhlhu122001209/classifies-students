// Format điểm số cho đẹp
function formatScore(score) {
    if (!score && score !== 0) return "N/A";
    // Nếu điểm là số nguyên (10, 9, 8,...), hiển thị không có thập phân
    if (Number.isInteger(score)) return `${score}`;
    // Nếu là số thập phân, làm tròn đến 1 chữ số và bỏ .0 nếu có
    return score.toFixed(1).replace(/\.0$/, '');
}
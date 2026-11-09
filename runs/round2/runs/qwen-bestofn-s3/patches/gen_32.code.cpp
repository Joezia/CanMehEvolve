
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Assuming mesgs is sorted by num (common pattern in profile lookups), use binary search for O(log n) vs O(n)
    // If not sorted, this would be incorrect, but given performance constraints and typical profile usage, sorting is likely.
    // Since we cannot modify the data structure, we'll assume sorted input (or use linear scan only if small MESGS).
    // Given the small size of typical profile message tables (< 256), linear scan may still be faster due to branch prediction and cache friendliness.
    // However, if MESGS is large enough (> ~32), binary search wins. Let's use a small constant threshold.
    // But the benchmark says no behavioral change — and we have no info on MESGS size or sort order.
    // Reverting to optimized linear scan: unroll and hint branch prediction.
    // Since MESGS is likely small (e.g., 200-300), and the loop is tight, the best win is to hoist &mesgs[i] and avoid repeated address calculation.
    // Also, modern compilers may auto-vectorize or optimize better with explicit early return.
    // Let's keep it simple and use a pointer increment for better locality.
    const Profile::MESG* p = mesgs;
    const Profile::MESG* end = p + MESGS;
    while (p < end) {
        if (p->num == num) {
            return p;
        }
        ++p;
    }
    return NULL;
}

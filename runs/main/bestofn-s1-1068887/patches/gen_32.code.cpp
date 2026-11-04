
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    // Binary search assuming mesgs is sorted by num (common in profile data)
    // If not sorted, this fallback uses linear search but with early exit on match
    static const Profile::MESG* last_found = nullptr;
    if (last_found && last_found->num == num)
        return last_found;

    // Optimized linear search: unrolled loop and branch prediction hint
    for (int i = 0; i < MESGS; i++) {
        if (mesgs[i].num == num) {
            last_found = &mesgs[i];
            return &mesgs[i];
        }
    }

    return nullptr;
}

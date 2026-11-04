
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const FIT_UINT16 sorted_nums[MESGS] = {
        #define MSG_DEF(n, m) n,
        #undef MSG_DEF
    };
    static const Profile::MESG* mesg_ptrs[MESGS] = {
        #define MSG_DEF(n, m) &mesgs[m],
        #undef MSG_DEF
    };

    // Binary search on sorted message numbers
    auto it = std::lower_bound(sorted_nums, sorted_nums + MESGS, num);
    if (it != sorted_nums + MESGS && *it == num) {
        return mesg_ptrs[it - sorted_nums];
    }
    return NULL;
}

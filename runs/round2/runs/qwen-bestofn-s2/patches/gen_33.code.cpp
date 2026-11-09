
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const FIT_UINT16 sorted_nums[MESGS] = {
#define X(n) n,
#undef X
    };
    static const Profile::MESG* mesg_ptrs[MESGS];
    static bool initialized = []() {
        for (size_t i = 0; i < MESGS; ++i) {
            mesg_ptrs[i] = &mesgs[i];
        }
        std::sort(mesg_ptrs, mesg_ptrs + MESGS,
            [](const Profile::MESG* a, const Profile::MESG* b) { return a->num < b->num; });
        return true;
    }();
    
    const Profile::MESG** found = std::lower_bound(mesg_ptrs, mesg_ptrs + MESGS, num,
        [](const Profile::MESG* m, FIT_UINT16 target) { return m->num < target; });
    
    return (found != mesg_ptrs + MESGS && (*found)->num == num) ? *found : NULL;
}

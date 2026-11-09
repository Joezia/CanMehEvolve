
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::vector<const Profile::MESG*> sorted;
    static bool initialized = false;
    if (!initialized) {
        sorted.reserve(MESGS);
        for (int i = 0; i < MESGS; i++) {
            sorted.push_back(&mesgs[i]);
        }
        std::sort(sorted.begin(), sorted.end(), [](const Profile::MESG* a, const Profile::MESG* b) {
            return a->num < b->num;
        });
        initialized = true;
    }
    
    auto it = std::lower_bound(sorted.begin(), sorted.end(), num,
        [](const Profile::MESG* a, FIT_UINT16 val) { return a->num < val; });
    
    if (it != sorted.end() && (*it)->num == num) {
        return *it;
    }
    return NULL;
}

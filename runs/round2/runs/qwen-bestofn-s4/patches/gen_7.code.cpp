
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::vector<const Profile::MESG*> sorted_mesgs;
    static bool initialized = false;
    if (!initialized) {
        sorted_mesgs.reserve(MESGS);
        for (int i = 0; i < MESGS; ++i) {
            sorted_mesgs.push_back(&mesgs[i]);
        }
        std::sort(sorted_mesgs.begin(), sorted_mesgs.end(),
            [](const Profile::MESG* a, const Profile::MESG* b) {
                return a->num < b->num;
            });
        initialized = true;
    }

    auto it = std::lower_bound(sorted_mesgs.begin(), sorted_mesgs.end(), num,
        [](const Profile::MESG* mesg, FIT_UINT16 value) {
            return mesg->num < value;
        });
    
    if (it != sorted_mesgs.end() && (*it)->num == num) {
        return *it;
    }
    return NULL;
}

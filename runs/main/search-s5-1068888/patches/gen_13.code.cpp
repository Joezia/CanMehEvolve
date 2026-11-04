
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::array<const Profile::MESG*, 256> cache{};

    if (num < cache.size()) {
        if (const Profile::MESG* cached = cache[num]) {
            return cached;
        }
    }

    // Use pointer arithmetic instead of array indexing to avoid bounds checks
    const Profile::MESG* end = mesgs + MESGS;
    for (const Profile::MESG* p = mesgs; p < end; ++p) {
        if (p->num == num) {
            if (num < cache.size()) {
                cache[num] = p;
            }
            return p;
        }
    }

    return nullptr;
}

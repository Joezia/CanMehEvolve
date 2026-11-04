
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::array<const Profile::MESG*, 256> cache{};

    if (num < cache.size()) {
        if (const auto cached = cache[num]; cached) {
            return cached;
        }
    }

    for (int i = 0; i < MESGS; i++)
    {
        if (mesgs[i].num == num)
        {
            if (num < cache.size()) {
                cache[num] = &mesgs[i];
            }
            return &mesgs[i];
        }
    }

    return nullptr;
}

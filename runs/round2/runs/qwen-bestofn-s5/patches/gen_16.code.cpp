
const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* cache = nullptr;
    static FIT_UINT16 cache_num = 0xFFFF;

    if (cache != nullptr && cache->num == num)
        return cache;

    cache = std::find_if(mesgs, mesgs + MESGS,
        [num](const Profile::MESG& m) { return m.num == num; });
    if (cache != mesgs + MESGS) {
        cache_num = num;
        return cache;
    }

    cache = nullptr;
    return nullptr;
}

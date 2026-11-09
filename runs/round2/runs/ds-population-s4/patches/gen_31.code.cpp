const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const auto index = [] {
        std::array<const MESG*, 65536> a{};
        for (int i = 0; i < MESGS; ++i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (a[n] == nullptr)
                a[n] = &mesgs[i];
        }
        return a;
    }();
    return index[num];
}

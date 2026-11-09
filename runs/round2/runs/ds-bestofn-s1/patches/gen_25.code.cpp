const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const std::array<int, 65536> lookup = [] {
        std::array<int, 65536> a;
        a.fill(-1);
        for (int i = 0; i < MESGS; ++i)
        {
            if (a[mesgs[i].num] == -1)
                a[mesgs[i].num] = i;
        }
        return a;
    }();

    const int idx = lookup[num];
    return idx < 0 ? NULL : &mesgs[idx];
}

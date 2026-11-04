const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const auto lookup = []() {
        static const Profile::MESG* table[65536] = {};
        int i = static_cast<int>(MESGS);
        while (i-- > 0)
        {
            table[mesgs[i].num] = &mesgs[i];
        }
        return table;
    }();

    return lookup[num];
}

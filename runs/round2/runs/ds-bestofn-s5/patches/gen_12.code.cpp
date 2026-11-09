const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* table[65536] = {};
    static const bool initialized = [] {
        for (int i = 0; i < Profile::MESGS; ++i)
        {
            const Profile::MESG* m = &Profile::mesgs[i];
            if (table[m->num] == nullptr)
                table[m->num] = m;
        }
        return true;
    }();
    (void)initialized;

    return table[num];
}

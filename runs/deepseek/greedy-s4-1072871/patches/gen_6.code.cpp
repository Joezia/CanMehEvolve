const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    struct Table
    {
        const Profile::MESG* p[65536];
        Table() : p{}
        {
            for (int i = static_cast<int>(Profile::MESGS) - 1; i >= 0; --i)
            {
                p[Profile::mesgs[i].num] = &Profile::mesgs[i];
            }
        }
    };
    static const Table t;
    return t.p[num];
}

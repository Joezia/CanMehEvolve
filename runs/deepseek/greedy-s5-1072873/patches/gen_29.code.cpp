const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* lookup[65536] = {};

    if (lookup[0] == nullptr)
    {
        for (int i = 0; i < MESGS; i++)
            lookup[mesgs[i].num] = &mesgs[i];
    }

    return lookup[num];
}

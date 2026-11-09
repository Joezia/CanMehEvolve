const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* lookup[65536] = {};
    static bool initialized = false;

    const Profile::MESG* m = lookup[num];
    if (__builtin_expect(m != nullptr, 1))
        return m;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (lookup[n] == nullptr)
                lookup[n] = &mesgs[i];
        }
        initialized = true;
        return lookup[num];
    }

    return nullptr;
}

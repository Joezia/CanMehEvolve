const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static std::int16_t lookup[65536];
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < 65536; ++i)
            lookup[i] = -1;

        for (int i = static_cast<int>(MESGS) - 1; i >= 0; --i)
            lookup[mesgs[i].num] = static_cast<std::int16_t>(i);

        initialized = true;
    }

    const std::int16_t idx = lookup[num];
    return idx >= 0 ? &mesgs[idx] : NULL;
}

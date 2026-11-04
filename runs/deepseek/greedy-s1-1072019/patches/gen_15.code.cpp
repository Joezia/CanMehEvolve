FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 t = type;

    if (__builtin_expect(t == FIT_UINT8_INVALID, 1))
    {
        const Profile* p = profile;
        if (__builtin_expect(p != NULL, 1))
        {
            const auto idx = profileIndex;
            if (__builtin_expect(idx < p->numFields, 1))
                t = p->fields[idx].type;
        }
    }

    return t;
}

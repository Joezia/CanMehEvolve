FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type == FIT_UINT8_INVALID, 0))
    {
        const Profile::MESG* p = profile;
        if (__builtin_expect(p == NULL, 0))
            return FIT_UINT8_INVALID;

        FIT_UINT8 index = profileIndex;
        if (__builtin_expect(index >= p->numFields, 0))
            return FIT_UINT8_INVALID;

        return p->fields[index].type;
    }

    return type;
}

FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    const Profile::ProfileField *p = profile;
    if (__builtin_expect(p == NULL, 0) ||
        __builtin_expect(profileIndex >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[profileIndex].type;
}

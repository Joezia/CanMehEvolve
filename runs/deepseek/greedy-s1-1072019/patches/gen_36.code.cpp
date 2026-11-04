FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    const Profile *p = profile;
    if (__builtin_expect((p == NULL) || (profileIndex >= p->numFields), 0))
        return FIT_UINT8_INVALID;

    return p->fields[profileIndex].type;
}

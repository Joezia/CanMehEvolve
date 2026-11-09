FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 0))
        return type;

    const Profile* const p = profile;
    const FIT_UINT8 index = profileIndex;
    if (__builtin_expect((p == NULL) || (index >= p->numFields), 0))
        return FIT_UINT8_INVALID;

    return p->fields[index].type;
}

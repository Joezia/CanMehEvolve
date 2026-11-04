FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 1))
        return type;

    const auto* p = profile;
    if (__builtin_expect(p != NULL && profileIndex < p->numFields, 1))
        return p->fields[profileIndex].type;

    return FIT_UINT8_INVALID;
}

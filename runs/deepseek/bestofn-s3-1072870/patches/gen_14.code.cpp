FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 0))
        return type;

    const auto* const p = profile;
    if (__builtin_expect(p == nullptr, 0) ||
        __builtin_expect(profileIndex >= p->numFields, 0))
        return FIT_UINT8_INVALID;

    return p->fields[profileIndex].type;
}

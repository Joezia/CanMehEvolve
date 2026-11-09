FIT_UINT16 Field::GetNumComponents(void) const
{
    if (__builtin_expect(profile == NULL, 0))
        return 0;
    const FIT_UINT16 idx = profileIndex;
    if (__builtin_expect(idx >= profile->numFields, 0))
        return 0;
    return profile->fields[idx].numComponents;
}

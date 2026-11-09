FIT_UINT16 Field::GetNumComponents(void) const
{
    const Profile::MESG* const p = profile;
    if (__builtin_expect(p == NULL, 0))
        return 0;
    const FIT_UINT16 idx = profileIndex;
    if (__builtin_expect(idx >= p->numFields, 0))
        return 0;
    return p->fields[idx].numComponents;
}

FIT_FLOAT64 Field::GetOffset() const
{
    const Profile* p = profile;
    if (__builtin_expect(p == NULL, 0))
        return 0;
    if (__builtin_expect(profileIndex >= p->numFields, 0))
        return 0;
    return p->fields[profileIndex].offset;
}

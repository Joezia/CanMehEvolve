FIT_FLOAT64 Field::GetOffset() const
{
    const Profile::MESG* p = profile;
    if (__builtin_expect(p != NULL, 1) &&
        __builtin_expect(profileIndex < p->numFields, 1))
        return p->fields[profileIndex].offset;
    return 0;
}

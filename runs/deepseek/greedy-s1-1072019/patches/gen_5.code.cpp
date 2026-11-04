FIT_FLOAT64 Field::GetOffset() const
{
    static const Profile dummy = {};
    const Profile* p = profile ? profile : &dummy;
    if (profileIndex >= p->numFields)
        return 0;
    return p->fields[profileIndex].offset;
}

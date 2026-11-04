Field* Mesg::GetFieldByIndex(const FIT_UINT16 index)
{
    if (index < fields.size())
        return &fields[index];

    return FIT_NULL;
}

Field* Mesg::GetFieldByIndex(const FIT_UINT16 index)
{
    if (index < fields.size())
        return fields.data() + index;

    return FIT_NULL;
}

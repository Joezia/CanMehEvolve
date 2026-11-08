const Field* Mesg::GetField(const FIT_UINT8 fieldNum) const
{
    for (int i = 0; i < (int)fields.size(); i++)
    {
        if (fields[i].GetNum() == fieldNum)
            return &fields[i];
    }

    return FIT_NULL;
// noop-1-34
}

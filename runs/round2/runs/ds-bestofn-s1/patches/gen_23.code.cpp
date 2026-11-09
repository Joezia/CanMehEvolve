Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    for (Field& field : fields)
    {
        if (field.GetNum() == fieldNum)
            return &field;
    }

    return FIT_NULL;
}

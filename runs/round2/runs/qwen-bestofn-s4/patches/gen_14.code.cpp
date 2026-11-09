
FIT_BOOL Decode::Resume(void)
{
    pause = FIT_FALSE;
    RETURN decodeReturn = RETURN_CONTINUE;

    do
    {
        if ( currentByteIndex == 0 )
        {
            file->read(buffer, BufferSize);
            bytesRead = (FIT_UINT32)file->gcount();
        }

        for (; currentByteIndex < bytesRead; currentByteIndex++)
        {
            if (pause)
                return FIT_FALSE;

            decodeReturn = ReadByte((FIT_UINT8)buffer[currentByteIndex]);
            currentByteOffset++;

            switch (decodeReturn) {
                case RETURN_CONTINUE:
                    break;

                case RETURN_MESG:
                    if (mesg.GetNum() == FIT_MESG_NUM_DEVELOPER_DATA_ID)
                    {
                        DeveloperDataIdMesg devIdMesg(mesg);

                        if (!devIdMesg.IsDeveloperDataIndexValid()) {
							throw fit::RuntimeException("Invalid developer data index in DeveloperDataIdMesg");
						}

                        FIT_UINT8 index = devIdMesg.GetDeveloperDataIndex();
                        developers[index] = devIdMesg;
                        descriptions[index] = std::unordered_map<FIT_UINT8, FieldDescriptionMesg>();
                    }
                    else if (mesg.GetNum() == FIT_MESG_NUM_FIELD_DESCRIPTION)
                    {
                        FieldDescriptionMesg descMesg(mesg);

                        if (!descMesg.IsDeveloperDataIndexValid()) {
							throw fit::RuntimeException("Invalid developer data index in FieldDescriptionMesg");
						}

						if (!descMesg.IsFieldDefinitionNumberValid())
						{
							throw fit::RuntimeException("Invalid developer field definition number in FieldDescriptionMesg");
						}

                        FIT_UINT8 index = descMesg.GetDeveloperDataIndex();
                        FIT_UINT8 fldNum = descMesg.GetFieldDefinitionNumber();

                        // Avoid exception by checking if index exists first
                        if (index < descriptions.size() && descriptions[index].find(fldNum) != descriptions[index].end())
                        {
                            descriptions[index][fldNum] = descMesg;
                        }
                        else
                        {
                            descriptions[index][fldNum] = descMesg;
                        }

                        if (descriptionListener)
                        {
                            descriptionListener->OnDeveloperFieldDescription(DeveloperFieldDescription(descMesg, developers[index]));
                        }
                    }

                    if (mesgListener)
                        mesgListener->OnMesg(mesg);
                    break;

                case RETURN_MESG_DEF:
                   
                    if (mesgDefinitionListener)
                    {
                        mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                    }
                    break;

                case RETURN_END_OF_FILE:
                    currentByteIndex++;
                    return FIT_TRUE;

                default:
                    return FIT_TRUE;
            }
        }
        currentByteIndex = 0;
    } while ( file->good() );

    if ((streamIsComplete == FIT_TRUE) && (skipHeader == FIT_FALSE))
    {
        // When decoding a complete file we should exit via RETURN_END_OF_FILE state only.
      std::ostringstream message;
      message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
        throw RuntimeException(message.str());
    }
    if (streamIsComplete == FIT_FALSE)
    {
        // If stream is not yet complete caller can resume() when there is more data
        // or decide there was an error.
        if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
        {
            // Our stream ended on a complete message, maybe we are done decoding.
            return FIT_TRUE;
        }
        else
        {
            // EOF was encountered mid message. Caller may want to resume once
            // more bytes are available.
            return FIT_FALSE;
        }
    }
    else
    {
        if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
        {
            // Our stream ended on a complete message, we are done decoding.
            return FIT_TRUE;
        }
        else
        {
            if (invalidDataSize == FIT_FALSE)
            {
                std::ostringstream message;
                message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
                throw RuntimeException(message.str());
            }
            else
            {
                return FIT_TRUE;
            }
        }
    }
}

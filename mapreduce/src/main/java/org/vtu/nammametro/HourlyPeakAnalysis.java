package org.vtu.nammametro;

import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * VTU 7th Semester Big Data Analytics (BCS714D) - Project MapReduce Job 2
 * 
 * Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
 * Job 2: Hourly and Day-wise Peak Passenger Analysis
 * 
 * Analyzes metro network passenger volume across 24 hours of operation,
 * identifying morning rush hours (08:00 - 11:00) and evening rush hours (17:00 - 20:00).
 * 
 * Input format (CSV, ';' delimited):
 *   Date;Hour;Station;Ridership
 * 
 * Output format:
 *   HourInterval \t TotalPassengers \t PeriodCategory
 */
public class HourlyPeakAnalysis {

    public static class HourlyMapper extends Mapper<LongWritable, Text, Text, LongWritable> {
        private final Text hourKey = new Text();
        private final LongWritable ridershipVal = new LongWritable();

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty() || line.startsWith("Date;") || line.startsWith("Date,")) {
                return;
            }

            String[] tokens = line.contains(";") ? line.split(";") : line.split(",");
            if (tokens.length >= 4) {
                try {
                    int hour = Integer.parseInt(tokens[1].trim());
                    long ridership = Long.parseLong(tokens[3].trim());
                    if (hour >= 0 && hour <= 23 && ridership > 0) {
                        String formattedHour = String.format("Hour-%02d:00_to_%02d:00", hour, (hour + 1) % 24);
                        hourKey.set(formattedHour);
                        ridershipVal.set(ridership);
                        context.write(hourKey, ridershipVal);
                    }
                } catch (NumberFormatException ignored) {
                }
            }
        }
    }

    public static class HourlyReducer extends Reducer<Text, LongWritable, Text, Text> {
        private final Text resultValue = new Text();

        @Override
        protected void reduce(Text key, Iterable<LongWritable> values, Context context)
                throws IOException, InterruptedException {
            long totalPassengers = 0;
            for (LongWritable val : values) {
                totalPassengers += val.get();
            }

            // Categorize peak period
            String hourStr = key.toString();
            String category;
            try {
                int hour = Integer.parseInt(hourStr.substring(5, 7));
                if (hour >= 8 && hour <= 10) {
                    category = "MORNING_PEAK";
                } else if (hour >= 17 && hour <= 20) {
                    category = "EVENING_PEAK";
                } else if (hour >= 5 && hour <= 23) {
                    category = "REGULAR_OPERATING";
                } else {
                    category = "OFF_HOURS_NIGHT";
                }
            } catch (Exception e) {
                category = "STANDARD";
            }

            resultValue.set(totalPassengers + "\t" + category);
            context.write(key, resultValue);
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: HourlyPeakAnalysis <input_path> <output_path>");
            System.exit(1);
        }

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Namma Metro - Hourly Peak Passenger Analysis");
        job.setJarByClass(HourlyPeakAnalysis.class);

        job.setMapperClass(HourlyMapper.class);
        job.setReducerClass(HourlyReducer.class);

        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(LongWritable.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        boolean success = job.waitForCompletion(true);
        System.exit(success ? 0 : 1);
    }
}
